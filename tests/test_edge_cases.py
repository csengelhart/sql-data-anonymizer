"""Tests for SQL escaping and special-value handling."""

import pytest
import sqlglot

from sqlglot import exp

from sql_anonymizer.transformer import InsertTransformer


def get_first_row_values(statement):
    """Return the values from the first INSERT row."""

    values_expression = statement.expression
    first_row = values_expression.expressions[0]

    return first_row.expressions


def test_original_name_with_apostrophe_is_anonymized():
    """An original apostrophe should not interfere with parsing."""

    sql = """
    INSERT INTO customers
        (customer_id, full_name, email)
    VALUES
        (
            102,
            'Jane O''Brien',
            'jane.obrien@example.com'
        );
    """

    statement = sqlglot.parse_one(sql, read="mysql")
    transformer = InsertTransformer(seed=499)

    transformed_statement = transformer.transform(statement)
    values = get_first_row_values(transformed_statement)

    assert values[1].this != "Jane O'Brien"
    assert values[2].this != "jane.obrien@example.com"

    # The transformed statement should still serialize as valid SQL.
    output_sql = transformed_statement.sql(dialect="mysql")
    reparsed_statement = sqlglot.parse_one(
        output_sql,
        read="mysql",
    )

    assert isinstance(reparsed_statement, exp.Insert)


def test_generated_name_with_apostrophe_is_escaped():
    """SQLGlot should safely serialize an apostrophe in generated data."""

    sql = """
    INSERT INTO customers
        (customer_id, full_name, email)
    VALUES
        (
            101,
            'John Smith',
            'john.smith@gmail.com'
        );
    """

    statement = sqlglot.parse_one(sql, read="mysql")
    transformer = InsertTransformer(seed=499)

    # Use a known generated value so this test always includes an apostrophe.
    def generate_name_with_apostrophe():
        return "Patrick O'Connor"

    transformer.generator.generate_name = (
        generate_name_with_apostrophe
    )

    transformed_statement = transformer.transform(statement)
    output_sql = transformed_statement.sql(dialect="mysql")

    # If escaping is correct, SQLGlot can parse its own output.
    reparsed_statement = sqlglot.parse_one(
        output_sql,
        read="mysql",
    )

    values = get_first_row_values(reparsed_statement)

    assert values[1].this == "Patrick O'Connor"
    assert values[2].this == "patrick.oconnor@example.com"


def test_null_values_remain_null():
    """NULL should not be replaced with synthetic data."""

    sql = """
    INSERT INTO customers
        (customer_id, full_name, address, email, phone)
    VALUES
        (
            103,
            'Carlos Rivera',
            NULL,
            NULL,
            NULL
        );
    """

    statement = sqlglot.parse_one(sql, read="mysql")
    transformer = InsertTransformer(seed=499)

    transformed_statement = transformer.transform(statement)
    values = get_first_row_values(transformed_statement)

    assert isinstance(values[2], exp.Null)
    assert isinstance(values[3], exp.Null)
    assert isinstance(values[4], exp.Null)


def test_empty_strings_remain_unchanged():
    """Empty and whitespace-only PII values should remain unchanged."""

    sql = """
    INSERT INTO customers
        (customer_id, full_name, email, phone)
    VALUES
        (
            104,
            '',
            '   ',
            ''
        );
    """

    statement = sqlglot.parse_one(sql, read="mysql")
    transformer = InsertTransformer(seed=499)

    transformed_statement = transformer.transform(statement)
    values = get_first_row_values(transformed_statement)

    assert values[1].this == ""
    assert values[2].this == "   "
    assert values[3].this == ""


def test_non_sensitive_punctuation_is_preserved():
    """Punctuation in a non-sensitive string should remain unchanged."""

    sql = """
    INSERT INTO shipping
        (
            shipping_id,
            recipient_name,
            delivery_instructions
        )
    VALUES
        (
            9001,
            'John Smith',
            'Leave at desk, ring bell, and don''t call.'
        );
    """

    statement = sqlglot.parse_one(sql, read="mysql")
    transformer = InsertTransformer(seed=499)

    transformed_statement = transformer.transform(statement)
    values = get_first_row_values(transformed_statement)

    assert values[1].this != "John Smith"

    assert values[2].this == (
        "Leave at desk, ring bell, and don't call."
    )


def test_insert_select_is_rejected():
    """INSERT SELECT is outside the supported project scope."""

    sql = """
    INSERT INTO archived_customers
        (customer_id, full_name)
    SELECT
        customer_id,
        full_name
    FROM customers;
    """

    statement = sqlglot.parse_one(sql, read="mysql")
    transformer = InsertTransformer(seed=499)

    with pytest.raises(
        ValueError,
        match="VALUES clause",
    ):
        transformer.transform(statement)