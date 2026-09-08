# SQL Data Anonymizer

A Python command-line application that replaces personally identifiable
information in MySQL files with realistic synthetic data while preserving
SQL structure, non-sensitive values, and repeated-value consistency.

This project was developed for the ICS 499 Software Engineering and
Capstone Project at Metro State University.

## Problem

Production database exports may contain personal information that should
not be distributed to developers, testers, students, or other users.

This application processes MySQL `CREATE TABLE` and
`INSERT INTO ... VALUES` statements and anonymizes four categories of PII:

- Names
- Addresses
- Email addresses
- Phone numbers

The program creates a separate anonymized SQL file that can be used for
software development and testing.

## Features

- Parses MySQL statements using SQLGlot
- Discovers column order from `CREATE TABLE` statements
- Supports INSERT statements with explicit column lists
- Supports INSERT statements without column lists
- Supports single-row and multi-row INSERT statements
- Generates realistic synthetic values with Faker
- Maintains consistent replacements across rows and tables
- Prevents different original values from sharing a replacement
- Generates emails that correspond to synthetic names
- Preserves common phone-number formats
- Preserves IDs, dates, totals, statuses, and other non-sensitive values
- Preserves `NULL`, empty, and whitespace-only values
- Safely handles apostrophes and other SQL string punctuation
- Supports an optional seed for repeatable testing

## Technologies

- Python 3.12
- Faker 40.38.0
- SQLGlot 30.18.0
- pytest 9.1.1
- MySQL 8.4 for independent output validation
- Git and GitHub for version control

## Project Structure

```text
sql-data-anonymizer/
├── sample_data/
│   ├── original.sql
│   └── anonymized.sql
├── src/
│   └── sql_anonymizer/
│       ├── __init__.py
│       ├── anonymizer.py
│       ├── classifier.py
│       ├── cli.py
│       ├── generator.py
│       ├── inspect_sql.py
│       ├── mapping.py
│       ├── schema.py
│       └── transformer.py
├── tests/
│   ├── test_anonymizer.py
│   ├── test_classifier.py
│   ├── test_edge_cases.py
│   ├── test_generator.py
│   ├── test_integration.py
│   ├── test_mapping.py
│   ├── test_schema.py
│   └── test_transformer.py
├── .gitignore
├── pyproject.toml
├── pytest.ini
├── README.md
└── requirements.txt