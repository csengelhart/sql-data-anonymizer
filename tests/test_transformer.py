"""Tests for transforming explicit single-row INSERT statements."""

import pytest
import sqlglot

from sqlglot import exp

from sql_anonymizer.schema import SchemaRegistry
from sql_anonymizer.transformer import InsertTransformer


def get_row_values(statement):
    """Return the values from the first row of an INSERT."""

    values_expression = statement.expression
    row = values_expression.expressions[0]

    return row.expressions


def test_sensitive_values_are_anonymized():
    """All four supported PII categories should be replaced."""

    sql = """
    INSERT INTO customers
        (customer_id, full_name, address, email, phone, account_status)
    VALUES
        (
            101,
            'John Smith',
            '123 Main Street, Minneapolis, MN 55401',
            'john.smith@gmail.com',
            '612-555-1234',
            'ACTIVE'
        );
    """

    statement = sqlglot.parse_one(sql, read="mysql")
    transformer = InsertTransformer(seed=499)

    transformed_statement = transformer.transform_single_row(statement)
    values = get_row_values(transformed_statement)

    assert values[1].this != "John Smith"
    assert values[2].this != "123 Main Street, Minneapolis, MN 55401"
    assert values[3].this != "john.smith@gmail.com"
    assert values[4].this != "612-555-1234"


def test_non_sensitive_values_are_preserved():
    """IDs and account-status values should remain unchanged."""

    sql = """
    INSERT INTO customers
        (customer_id, full_name, account_status)
    VALUES
        (101, 'John Smith', 'ACTIVE');
    """

    statement = sqlglot.parse_one(sql, read="mysql")
    transformer = InsertTransformer(seed=499)

    transformed_statement = transformer.transform_single_row(statement)
    values = get_row_values(transformed_statement)

    assert values[0].this == "101"
    assert values[2].this == "ACTIVE"


def test_email_matches_synthetic_name():
    """The generated email should correspond to the synthetic name."""

    sql = """
    INSERT INTO customers
        (customer_id, full_name, email)
    VALUES
        (101, 'John Smith', 'john.smith@gmail.com');
    """

    statement = sqlglot.parse_one(sql, read="mysql")
    transformer = InsertTransformer(seed=499)

    transformed_statement = transformer.transform_single_row(statement)
    values = get_row_values(transformed_statement)

    synthetic_name = values[1].this
    synthetic_email = values[2].this

    expected_email_name = synthetic_name.lower()
    expected_email_name = expected_email_name.replace("'", "")
    expected_email_name = expected_email_name.replace(" ", ".")

    expected_email = f"{expected_email_name}@example.com"

    assert synthetic_email == expected_email


def test_repeated_values_are_consistent_between_statements():
    """Repeated PII should receive the same replacements."""

    first_sql = """
    INSERT INTO customers
        (customer_id, full_name, email)
    VALUES
        (101, 'John Smith', 'john.smith@gmail.com');
    """

    second_sql = """
    INSERT INTO orders
        (order_id, customer_name, contact_email)
    VALUES
        (5001, 'John Smith', 'john.smith@gmail.com');
    """

    first_statement = sqlglot.parse_one(first_sql, read="mysql")
    second_statement = sqlglot.parse_one(second_sql, read="mysql")

    # Both statements must use the same transformer object.
    transformer = InsertTransformer(seed=499)

    first_result = transformer.transform_single_row(first_statement)
    second_result = transformer.transform_single_row(second_statement)

    first_values = get_row_values(first_result)
    second_values = get_row_values(second_result)

    assert first_values[1].this == second_values[1].this
    assert first_values[2].this == second_values[2].this


def test_null_phone_is_preserved():
    """A NULL phone value should remain NULL."""

    sql = """
    INSERT INTO customers
        (customer_id, full_name, phone)
    VALUES
        (103, 'Carlos Rivera', NULL);
    """

    statement = sqlglot.parse_one(sql, read="mysql")
    transformer = InsertTransformer(seed=499)

    transformed_statement = transformer.transform_single_row(statement)
    values = get_row_values(transformed_statement)

    assert isinstance(values[2], exp.Null)

def test_insert_without_columns_uses_table_schema():
    """An implicit INSERT should use columns from the schema registry."""

    sql = """
    INSERT INTO shipping
    VALUES
        (
            9001,
            101,
            'John Smith',
            '123 Main Street, Minneapolis, MN 55401',
            '612-555-1234',
            'Leave package at the front desk'
        );
    """

    statement = sqlglot.parse_one(sql, read="mysql")

    schema_registry = SchemaRegistry()

    schema_registry.register_table(
        "shipping",
        [
            "shipping_id",
            "customer_id",
            "recipient_name",
            "shipping_address",
            "contact_phone",
            "delivery_instructions",
        ],
    )

    transformer = InsertTransformer(seed=499)

    transformed_statement = transformer.transform_single_row(
        statement,
        schema_registry,
    )

    values = get_row_values(transformed_statement)

    # Sensitive values should change.
    assert values[2].this != "John Smith"
    assert values[3].this != (
        "123 Main Street, Minneapolis, MN 55401"
    )
    assert values[4].this != "612-555-1234"

    # Non-sensitive values should remain unchanged.
    assert values[0].this == "9001"
    assert values[1].this == "101"
    assert values[5].this == "Leave package at the front desk"

def test_implicit_insert_requires_schema_registry():
    """An implicit INSERT cannot be interpreted without its schema."""

    sql = """
    INSERT INTO shipping
    VALUES
        (
            9001,
            101,
            'John Smith',
            '123 Main Street',
            '612-555-1234',
            'Leave at front desk'
        );
    """

    statement = sqlglot.parse_one(sql, read="mysql")
    transformer = InsertTransformer(seed=499)

    with pytest.raises(
        ValueError,
        match="schema registry is required",
    ):
        transformer.transform_single_row(statement)

def test_implicit_insert_requires_known_table():
    """An implicit INSERT should fail if its table schema is unknown."""

    sql = """
    INSERT INTO unknown_table
    VALUES (101, 'John Smith');
    """

    statement = sqlglot.parse_one(sql, read="mysql")
    schema_registry = SchemaRegistry()
    transformer = InsertTransformer(seed=499)

    with pytest.raises(
        KeyError,
        match="No schema was found for table 'unknown_table'",
    ):
        transformer.transform_single_row(
            statement,
            schema_registry,
        )

def test_multiple_rows_are_rejected_for_now():
    """Multi-row INSERT support will be added in Step 10."""

    sql = """
    INSERT INTO customers
        (customer_id, full_name)
    VALUES
        (101, 'John Smith'),
        (102, 'Jane Doe');
    """

    statement = sqlglot.parse_one(sql, read="mysql")
    transformer = InsertTransformer(seed=499)

    with pytest.raises(
        ValueError,
        match="exactly one row",
    ):
        transformer.transform_single_row(statement)