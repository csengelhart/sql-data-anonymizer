"""Tests for complete SQL file anonymization."""

from pathlib import Path

import pytest
import sqlglot

from sqlglot import exp

from sql_anonymizer.anonymizer import anonymize_file


def test_anonymize_file_creates_output(tmp_path):
    """The program should create an anonymized SQL file."""

    input_file = tmp_path / "original.sql"
    output_file = tmp_path / "anonymized.sql"

    original_sql = """
    CREATE TABLE customers (
        customer_id INT,
        full_name VARCHAR(100),
        email VARCHAR(100),
        account_status VARCHAR(20)
    );

    INSERT INTO customers
    VALUES
        (
            101,
            'John Smith',
            'john.smith@gmail.com',
            'ACTIVE'
        );
    """

    input_file.write_text(
        original_sql,
        encoding="utf-8",
    )

    insert_count = anonymize_file(
        input_file,
        output_file,
        seed=499,
    )

    assert insert_count == 1
    assert output_file.exists()

    output_sql = output_file.read_text(encoding="utf-8")

    assert "John Smith" not in output_sql
    assert "john.smith@gmail.com" not in output_sql
    assert "ACTIVE" in output_sql
    assert "101" in output_sql


def test_output_file_contains_valid_sql(tmp_path):
    """The generated output should be parseable as MySQL."""

    input_file = tmp_path / "original.sql"
    output_file = tmp_path / "anonymized.sql"

    original_sql = """
    CREATE TABLE customers (
        customer_id INT,
        full_name VARCHAR(100)
    );

    INSERT INTO customers
    VALUES
        (101, 'Jane O''Brien');
    """

    input_file.write_text(
        original_sql,
        encoding="utf-8",
    )

    anonymize_file(
        input_file,
        output_file,
        seed=499,
    )

    output_sql = output_file.read_text(encoding="utf-8")

    statements = sqlglot.parse(
        output_sql,
        read="mysql",
    )

    assert len(statements) == 2
    assert isinstance(statements[0], exp.Create)
    assert isinstance(statements[1], exp.Insert)


def test_missing_input_file_raises_error(tmp_path):
    """A missing input file should produce a clear error."""

    input_file = tmp_path / "missing.sql"
    output_file = tmp_path / "anonymized.sql"

    with pytest.raises(
        FileNotFoundError,
        match="Input file was not found",
    ):
        anonymize_file(
            input_file,
            output_file,
            seed=499,
        )


def test_input_and_output_must_be_different(tmp_path):
    """The program should not overwrite its own input file."""

    sql_file = tmp_path / "original.sql"

    sql_file.write_text(
        "CREATE TABLE example (id INT);",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="input and output paths must be different",
    ):
        anonymize_file(
            sql_file,
            sql_file,
            seed=499,
        )


def test_empty_sql_file_raises_error(tmp_path):
    """An empty SQL file should not produce an output file."""

    input_file = tmp_path / "empty.sql"
    output_file = tmp_path / "anonymized.sql"

    input_file.write_text(
        "",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="contains no statements",
    ):
        anonymize_file(
            input_file,
            output_file,
            seed=499,
        )