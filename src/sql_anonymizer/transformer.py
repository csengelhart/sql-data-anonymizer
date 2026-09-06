"""Transform sensitive values inside SQL INSERT statements."""

from sqlglot import exp

from sql_anonymizer.classifier import ColumnClassifier
from sql_anonymizer.generator import SyntheticDataGenerator
from sql_anonymizer.mapping import MappingRegistry


class InsertTransformer:
    """Anonymize sensitive values in SQL INSERT statements."""

    def __init__(self, seed=None):
        self.classifier = ColumnClassifier()
        self.generator = SyntheticDataGenerator(seed)
        self.mapping_registry = MappingRegistry()

    def transform(self, statement, schema_registry=None):
        """Anonymize all rows in an INSERT statement."""

        if not isinstance(statement, exp.Insert):
            raise ValueError("The SQL statement must be an INSERT.")

        column_names = self._get_column_names(
            statement,
            schema_registry,
        )

        rows = self._get_rows(statement)

        for row in rows:
            if len(column_names) != len(row.expressions):
                raise ValueError(
                    "The number of columns does not match "
                    "the number of values."
                )

            self._anonymize_row(column_names, row)

        return statement

    def _get_column_names(self, statement, schema_registry):
        """Return explicit columns or retrieve them from the table schema."""

        insert_target = statement.this

        # An exp.Schema target means the INSERT declares its columns.
        if isinstance(insert_target, exp.Schema):
            column_names = []

            for column in insert_target.expressions:
                column_names.append(column.name.lower())

            return column_names

        # Without explicit columns, the INSERT target should be a table.
        if not isinstance(insert_target, exp.Table):
            raise ValueError(
                "Could not determine the INSERT table."
            )

        if schema_registry is None:
            raise ValueError(
                "A schema registry is required when an INSERT "
                "does not declare its columns."
            )

        table_name = insert_target.name

        return schema_registry.get_columns(table_name)

    def _get_rows(self, statement):
        """Return all rows from an INSERT VALUES statement."""

        values_expression = statement.expression

        if not isinstance(values_expression, exp.Values):
            raise ValueError(
                "The INSERT statement must contain a VALUES clause."
            )

        rows = values_expression.expressions

        if not rows:
            raise ValueError(
                "The INSERT statement must contain at least one row."
            )

        return rows

    def _anonymize_row(self, column_names, row):
        """Replace supported PII values in one row."""

        row_values = list(row.expressions)
        synthetic_name = None

        # Process names first so an email can use the synthetic name.
        for position in range(len(column_names)):
            column_name = column_names[position]
            category = self.classifier.classify(column_name)

            if category != "name":
                continue

            original_expression = row_values[position]

            if not self._is_string_value(original_expression):
                continue

            original_name = original_expression.this

            synthetic_name = self.mapping_registry.get_or_create(
                "name",
                original_name,
                self.generator.generate_name,
            )

            row_values[position] = exp.Literal.string(synthetic_name)

        # Process addresses, emails, and phone numbers.
        for position in range(len(column_names)):
            column_name = column_names[position]
            category = self.classifier.classify(column_name)

            if category not in {"address", "email", "phone"}:
                continue

            original_expression = row_values[position]

            if not self._is_string_value(original_expression):
                continue

            original_value = original_expression.this

            if category == "address":
                replacement = self.mapping_registry.get_or_create(
                    "address",
                    original_value,
                    self.generator.generate_address,
                )

            elif category == "email":

                def generate_email():
                    return self.generator.generate_email(synthetic_name)

                replacement = self.mapping_registry.get_or_create(
                    "email",
                    original_value,
                    generate_email,
                )

            else:

                def generate_phone():
                    return self.generator.generate_phone(original_value)

                replacement = self.mapping_registry.get_or_create(
                    "phone",
                    original_value,
                    generate_phone,
                )

            row_values[position] = exp.Literal.string(replacement)

        # Save the modified values back into the SQLGlot row.
        row.set("expressions", row_values)

    def _is_string_value(self, expression):
        """Return True when an SQL expression is a quoted string."""

        if not isinstance(expression, exp.Literal):
            return False

        return expression.is_string