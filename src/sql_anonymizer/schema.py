"""Discover and store table schemas from CREATE TABLE statements."""

from sqlglot import exp


class SchemaRegistry:
    """Store the column names belonging to each table."""

    def __init__(self):
        # Example:
        # {
        #     "customers": ["customer_id", "full_name", "email"],
        #     "orders": ["order_id", "customer_id", "order_total"]
        # }
        self.schemas = {}

    def register_table(self, table_name, column_names):
        """Save a table name and its columns."""

        # Normalize the table name so capitalization does not affect lookups.
        table_name = table_name.lower()

        normalized_columns = []

        # Normalize each column name for the same reason.
        for column_name in column_names:
            normalized_columns.append(column_name.lower())

        self.schemas[table_name] = normalized_columns

    def get_columns(self, table_name):
        """Return the columns registered for a table."""

        table_name = table_name.lower()

        if table_name not in self.schemas:
            raise KeyError(
                f"No schema was found for table '{table_name}'."
            )

        return self.schemas[table_name]

    def contains_table(self, table_name):
        """Return True if a table has been registered."""

        table_name = table_name.lower()

        return table_name in self.schemas


def discover_schemas(statements):
    """Find CREATE TABLE statements and register their columns."""

    registry = SchemaRegistry()

    for statement in statements:

        # Ignore INSERT statements and other non-CREATE statements.
        if not isinstance(statement, exp.Create):
            continue

        # Find the table being created.
        table = statement.find(exp.Table)

        # Skip the statement if SQLGlot did not find a table.
        if table is None:
            continue

        table_name = table.name
        column_names = []

        # Find each column definition inside the CREATE statement.
        for column_definition in statement.find_all(exp.ColumnDef):
            column_name = column_definition.this.name
            column_names.append(column_name)

        # Avoid registering CREATE statements that have no columns.
        if column_names:
            registry.register_table(table_name, column_names)

    return registry