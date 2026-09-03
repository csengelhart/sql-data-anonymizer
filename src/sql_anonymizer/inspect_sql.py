"""Explore how SQLGlot represents the project's sample MySQL statements."""

from pathlib import Path

import sqlglot
from sqlglot import exp


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SQL_FILE = PROJECT_ROOT / "sample_data" / "original.sql"


def inspect_create(statement: exp.Create) -> None:
    """Print the table and column information from a CREATE TABLE statement."""
    table = statement.find(exp.Table)

    print(f"Statement type: CREATE")
    print(f"Table: {table.name}")

    columns = list(statement.find_all(exp.ColumnDef))

    print("Columns:")

    for position, column in enumerate(columns):
        column_name = column.this.name
        data_type = column.args.get("kind")

        print(
            f"  Position {position}: "
            f"name={column_name}, "
            f"type={data_type.sql(dialect='mysql')}"
        )


def inspect_insert(statement: exp.Insert) -> None:
    """Print the table, declared columns, and rows from an INSERT statement."""
    table = statement.find(exp.Table)

    print("Statement type: INSERT")
    print(f"Table: {table.name}")

    insert_target = statement.this

    if isinstance(insert_target, exp.Schema):
        declared_columns = [
            column.name for column in insert_target.expressions
        ]
    else:
        declared_columns = []

    if declared_columns:
        print(f"Declared columns: {declared_columns}")
    else:
        print("Declared columns: none")

    values_expression = statement.expression

    if not isinstance(values_expression, exp.Values):
        print("This INSERT does not contain a supported VALUES clause.")
        return

    for row_number, row in enumerate(values_expression.expressions, start=1):
        values = [
            value.sql(dialect="mysql")
            for value in row.expressions
        ]

        print(f"  Row {row_number}: {values}")


def main() -> None:
    """Parse and inspect every statement in the sample SQL file."""
    sql_text = SQL_FILE.read_text(encoding="utf-8")
    statements = sqlglot.parse(sql_text, read="mysql")

    for statement_number, statement in enumerate(statements, start=1):
        print(f"\n--- Statement {statement_number} ---")

        if isinstance(statement, exp.Create):
            inspect_create(statement)
        elif isinstance(statement, exp.Insert):
            inspect_insert(statement)
        else:
            print(f"Unsupported statement type: {type(statement).__name__}")


if __name__ == "__main__":
    main()