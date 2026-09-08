"""Integration tests for the complete SQL anonymization process."""

from pathlib import Path

import sqlglot
from sqlglot import exp

from sql_anonymizer.anonymizer import anonymize_file


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_INPUT = PROJECT_ROOT / "sample_data" / "original.sql"


def create_anonymized_sample(tmp_path, seed=499):
    """Anonymize the sample SQL file and return parsed output."""

    output_file = tmp_path / "anonymized.sql"

    anonymize_file(
        SAMPLE_INPUT,
        output_file,
        seed=seed,
    )

    output_sql = output_file.read_text(encoding="utf-8")

    statements = sqlglot.parse(
        output_sql,
        read="mysql",
    )

    return output_sql, statements


def find_insert(statements, table_name):
    """Find the INSERT statement belonging to a table."""

    for statement in statements:
        if not isinstance(statement, exp.Insert):
            continue

        table = statement.find(exp.Table)

        if table is not None and table.name == table_name:
            return statement

    raise AssertionError(
        f"No INSERT statement was found for table '{table_name}'."
    )


def get_rows(insert_statement):
    """Return the rows contained in an INSERT statement."""

    values_expression = insert_statement.expression
    rows = []

    for row in values_expression.expressions:
        rows.append(row.expressions)

    return rows


def test_all_original_pii_is_removed(tmp_path):
    """None of the original targeted PII should remain in the output."""

    output_sql, statements = create_anonymized_sample(tmp_path)

    original_pii_values = [
        "John Smith",
        "Jane O'Brien",
        "Carlos Rivera",
        "123 Main Street, Minneapolis, MN 55401",
        "845 Grand Avenue, St. Paul, MN 55105",
        "2900 Lake Street, Minneapolis, MN 55408",
        "john.smith@gmail.com",
        "jane.obrien@yahoo.com",
        "carlos.rivera@example.org",
        "612-555-1234",
        "(651) 555-9876",
    ]

    for original_value in original_pii_values:
        assert original_value not in output_sql


def test_repeated_values_are_consistent_across_tables(tmp_path):
    """Repeated customer PII should match across all tables."""

    output_sql, statements = create_anonymized_sample(tmp_path)

    customers_insert = find_insert(statements, "customers")
    orders_insert = find_insert(statements, "orders")
    shipping_insert = find_insert(statements, "shipping")

    customer_rows = get_rows(customers_insert)
    order_rows = get_rows(orders_insert)
    shipping_rows = get_rows(shipping_insert)

    # John Smith appears in customer row 1, order rows 1 and 3,
    # and shipping row 1.
    john_customer_name = customer_rows[0][1].this
    john_customer_email = customer_rows[0][3].this

    assert order_rows[0][2].this == john_customer_name
    assert order_rows[2][2].this == john_customer_name
    assert shipping_rows[0][2].this == john_customer_name

    assert order_rows[0][3].this == john_customer_email
    assert order_rows[2][3].this == john_customer_email

    # John's address and phone should match between the two tables
    # where those values appear.
    assert shipping_rows[0][3].this == customer_rows[0][2].this
    assert shipping_rows[0][4].this == customer_rows[0][4].this

    # Jane's repeated information should also remain consistent.
    assert order_rows[1][2].this == customer_rows[1][1].this
    assert order_rows[1][3].this == customer_rows[1][3].this
    assert shipping_rows[1][2].this == customer_rows[1][1].this
    assert shipping_rows[1][3].this == customer_rows[1][2].this
    assert shipping_rows[1][4].this == customer_rows[1][4].this


def test_non_sensitive_values_are_preserved(tmp_path):
    """IDs and other business data should remain unchanged."""

    output_sql, statements = create_anonymized_sample(tmp_path)

    customers_insert = find_insert(statements, "customers")
    orders_insert = find_insert(statements, "orders")
    shipping_insert = find_insert(statements, "shipping")

    customer_rows = get_rows(customers_insert)
    order_rows = get_rows(orders_insert)
    shipping_rows = get_rows(shipping_insert)

    # Customer IDs and statuses.
    assert customer_rows[0][0].this == "101"
    assert customer_rows[0][5].this == "ACTIVE"

    assert customer_rows[1][0].this == "102"
    assert customer_rows[1][5].this == "ACTIVE"

    assert customer_rows[2][0].this == "103"
    assert customer_rows[2][5].this == "INACTIVE"

    # Order IDs, customer IDs, totals, and dates.
    assert order_rows[0][0].this == "5001"
    assert order_rows[0][1].this == "101"
    assert order_rows[0][4].this == "149.99"
    assert order_rows[0][5].this == "2026-08-15"

    assert order_rows[1][0].this == "5002"
    assert order_rows[1][1].this == "102"
    assert order_rows[1][4].this == "87.50"
    assert order_rows[1][5].this == "2026-08-16"

    assert order_rows[2][0].this == "5003"
    assert order_rows[2][1].this == "101"
    assert order_rows[2][4].this == "42.75"
    assert order_rows[2][5].this == "2026-08-17"

    # Shipping IDs, customer IDs, and delivery instructions.
    assert shipping_rows[0][0].this == "9001"
    assert shipping_rows[0][1].this == "101"
    assert shipping_rows[0][5].this == (
        "Leave package at the front desk"
    )

    assert shipping_rows[1][0].this == "9002"
    assert shipping_rows[1][1].this == "102"
    assert shipping_rows[1][5].this == "Signature required"

    assert shipping_rows[2][0].this == "9003"
    assert shipping_rows[2][1].this == "103"
    assert isinstance(shipping_rows[2][5], exp.Null)


def test_statement_and_row_counts_are_preserved(tmp_path):
    """The output should retain every SQL statement and data row."""

    original_sql = SAMPLE_INPUT.read_text(encoding="utf-8")

    original_statements = sqlglot.parse(
        original_sql,
        read="mysql",
    )

    output_sql, output_statements = create_anonymized_sample(tmp_path)

    assert len(output_statements) == len(original_statements)

    original_insert_count = 0
    output_insert_count = 0
    original_row_count = 0
    output_row_count = 0

    for statement in original_statements:
        if isinstance(statement, exp.Insert):
            original_insert_count += 1
            original_row_count += len(
                statement.expression.expressions
            )

    for statement in output_statements:
        if isinstance(statement, exp.Insert):
            output_insert_count += 1
            output_row_count += len(
                statement.expression.expressions
            )

    assert output_insert_count == original_insert_count
    assert output_row_count == original_row_count

    assert output_insert_count == 3
    assert output_row_count == 9


def test_different_customers_receive_unique_values(tmp_path):
    """Different customers should receive different synthetic PII."""

    output_sql, statements = create_anonymized_sample(tmp_path)

    customers_insert = find_insert(statements, "customers")
    customer_rows = get_rows(customers_insert)

    names = set()
    addresses = set()
    emails = set()

    for row in customer_rows:
        names.add(row[1].this)
        addresses.add(row[2].this)
        emails.add(row[3].this)

    assert len(names) == 3
    assert len(addresses) == 3
    assert len(emails) == 3


def test_same_seed_produces_same_output(tmp_path):
    """Using the same seed should produce repeatable output."""

    first_output_file = tmp_path / "first_anonymized.sql"
    second_output_file = tmp_path / "second_anonymized.sql"

    anonymize_file(
        SAMPLE_INPUT,
        first_output_file,
        seed=499,
    )

    anonymize_file(
        SAMPLE_INPUT,
        second_output_file,
        seed=499,
    )

    first_output = first_output_file.read_text(encoding="utf-8")
    second_output = second_output_file.read_text(encoding="utf-8")

    assert first_output == second_output