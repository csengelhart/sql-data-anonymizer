"""Tests for SQL schema discovery."""

import pytest
import sqlglot

from sql_anonymizer.schema import SchemaRegistry
from sql_anonymizer.schema import discover_schemas


def test_register_and_retrieve_table_schema():
    """A registered schema should retain its column order."""

    registry = SchemaRegistry()

    registry.register_table(
        "customers",
        ["customer_id", "full_name", "email"],
    )

    assert registry.get_columns("customers") == [
        "customer_id",
        "full_name",
        "email",
    ]


def test_table_lookup_is_case_insensitive():
    """Table lookup should work regardless of capitalization."""

    registry = SchemaRegistry()

    registry.register_table(
        "Customers",
        ["Customer_ID", "Full_Name"],
    )

    assert registry.contains_table("CUSTOMERS")

    assert registry.get_columns("customers") == [
        "customer_id",
        "full_name",
    ]


def test_unknown_table_raises_clear_error():
    """Requesting an unknown table should raise a clear error."""

    registry = SchemaRegistry()

    with pytest.raises(
        KeyError,
        match="No schema was found for table 'missing_table'",
    ):
        registry.get_columns("missing_table")


def test_discover_schemas_from_create_tables():
    """CREATE TABLE statements should populate the registry."""

    sql = """
    CREATE TABLE customers (
        customer_id INT PRIMARY KEY,
        full_name VARCHAR(100),
        email VARCHAR(100)
    );

    CREATE TABLE orders (
        order_id INT PRIMARY KEY,
        customer_id INT,
        order_total DECIMAL(10, 2),
        FOREIGN KEY (customer_id)
            REFERENCES customers(customer_id)
    );
    """

    statements = sqlglot.parse(sql, read="mysql")

    registry = discover_schemas(statements)

    assert registry.get_columns("customers") == [
        "customer_id",
        "full_name",
        "email",
    ]

    assert registry.get_columns("orders") == [
        "order_id",
        "customer_id",
        "order_total",
    ]


def test_non_create_statements_are_ignored():
    """INSERT statements should not be registered as schemas."""

    sql = """
    INSERT INTO customers
    VALUES (101, 'John Smith');
    """

    statements = sqlglot.parse(sql, read="mysql")

    registry = discover_schemas(statements)

    assert not registry.contains_table("customers")