"""Process an SQL file and create an anonymized copy."""

from pathlib import Path

import sqlglot
from sqlglot import exp

from sql_anonymizer.schema import discover_schemas
from sql_anonymizer.transformer import InsertTransformer


def anonymize_file(input_path, output_path, seed=None):
    """Read, anonymize, and write an SQL file."""

    input_path = Path(input_path)
    output_path = Path(output_path)

    validate_file_paths(input_path, output_path)

    sql_text = input_path.read_text(encoding="utf-8")

    # Reject files that are empty or contain only whitespace.
    if not sql_text.strip():
        raise ValueError(
            "The input SQL file contains no statements."
        )

    parsed_statements = sqlglot.parse(
        sql_text,
        read="mysql",
    )

    # SQLGlot may return None for content that is not an SQL statement.
    statements = []

    for statement in parsed_statements:
        if statement is not None:
            statements.append(statement)

    if not statements:
        raise ValueError(
            "The input SQL file contains no statements."
        )

    schema_registry = discover_schemas(statements)
    transformer = InsertTransformer(seed)

    insert_count = 0

    for statement in statements:
        if isinstance(statement, exp.Insert):
            transformer.transform(
                statement,
                schema_registry,
            )

            insert_count += 1

    output_sql = build_output_sql(statements)

    # Create the output directory if it does not exist.
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        output_sql,
        encoding="utf-8",
    )

    return insert_count


def validate_file_paths(input_path, output_path):
    """Validate the input and output file paths."""

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file was not found: {input_path}"
        )

    if not input_path.is_file():
        raise ValueError(
            f"Input path is not a file: {input_path}"
        )

    if input_path.resolve() == output_path.resolve():
        raise ValueError(
            "The input and output paths must be different."
        )


def build_output_sql(statements):
    """Convert parsed statements back into formatted MySQL."""

    formatted_statements = []

    for statement in statements:
        formatted_sql = statement.sql(
            dialect="mysql",
            pretty=True,
        )

        formatted_statements.append(formatted_sql)

    # Add a semicolon and blank line between statements.
    output_sql = ";\n\n".join(formatted_statements)

    # End the final statement with a semicolon and newline.
    output_sql += ";\n"

    return output_sql