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

## Installation

### Prerequisites

* Python 3.12 or newer
* Git
* MySQL 8.4 or Docker for optional database validation

### Clone the repository

```powershell
git clone YOUR_GITHUB_REPOSITORY_URL
cd sql-data-anonymizer
```

### Create and activate a virtual environment

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

Verify the installation:

```powershell
sql-anonymizer --help
```

## Usage

Run the program by providing an input SQL file and a different output path:

```powershell
sql-anonymizer sample_data/original.sql sample_data/anonymized.sql
```

Successful output resembles:

```text
Anonymization complete. Processed 3 INSERT statements.
Output written to: sample_data/anonymized.sql
```

An optional seed can produce repeatable synthetic values for testing.

```powershell
sql-anonymizer sample_data/original.sql sample_data/anonymized.sql --seed 499
```

A fixed seed is intended for testing and demonstrations.

## Expected Input

The program accepts a MySQL SQL file containing `CREATE TABLE` and `INSERT INTO ... VALUES` statements.

Example:

```sql
CREATE TABLE customers (
    customer_id INT,
    full_name VARCHAR(100),
    address VARCHAR(200),
    email VARCHAR(100),
    phone VARCHAR(30)
);

INSERT INTO customers
VALUES
    (
        101,
        'John Smith',
        '123 Main Street, Minneapolis, MN 55401',
        'john.smith@gmail.com',
        '612-555-1234'
    );
```

The application supports:

* Explicit and implicit INSERT column lists
* Single-row and multi-row INSERT statements
* Multiple tables
* SQL `NULL` values
* Apostrophes and punctuation in SQL strings

## Generated Output

The program creates a new SQL file containing realistic synthetic PII:

```sql
CREATE TABLE customers (
    customer_id INT,
    full_name VARCHAR(100),
    address VARCHAR(200),
    email VARCHAR(100),
    phone VARCHAR(30)
);

INSERT INTO customers
VALUES
    (
        101,
        'Daniel Christensen',
        '9748 Grace Glen Apt. 464, Figueroaview, NV 41373',
        'daniel.christensen@example.com',
        '964-555-7372'
    );
```

The original file is not overwritten. Non-sensitive values such as IDs, dates, totals, statuses, and foreign keys remain unchanged.

## Anonymization Strategy

The application uses consistent pseudonymization with realistic synthetic replacement data.

The processing sequence is:

1. Read the input SQL file.
2. Parse the SQL using the MySQL dialect.
3. Discover tables and their column order from `CREATE TABLE`.
4. Classify columns as name, address, email, phone, or non-sensitive.
5. Generate realistic replacements with Faker.
6. Store mappings for repeated values.
7. Modify only targeted values in INSERT statements.
8. Serialize the syntax trees back into valid MySQL.
9. Write the result to a separate output file.

Commonly recognized columns include:

| Category | Example column names                                                                  |
| -------- | ------------------------------------------------------------------------------------- |
| Name     | `name`, `full_name`, `customer_name`, `contact_name`, `recipient_name`                |
| Address  | `address`, `street_address`, `mailing_address`, `shipping_address`, `billing_address` |
| Email    | `email`, `email_address`, `contact_email`                                             |
| Phone    | `phone`, `phone_number`, `contact_phone`, `mobile_phone`, `telephone`                 |

Exact column-name matching reduces false positives such as `username`, `product_name`, and `ip_address`.

SQLGlot parses SQL into syntax trees, allowing the application to change targeted values without performing unrestricted text replacement.

## Consistency

The program maintains a separate in-memory mapping dictionary for each PII category.

For example:

```text
John Smith → Daniel Christensen
```

Every later occurrence of `John Smith` receives `Daniel Christensen`, including occurrences in other tables.

The same behavior applies independently to:

* Names
* Addresses
* Email addresses
* Phone numbers

The program also tracks used synthetic values so two different original values do not accidentally receive the same replacement.

When a name and email appear in the same record, the email is based on the synthetic name:

```text
Daniel Christensen
daniel.christensen@example.com
```

The same transformer and mapping registry are used for the entire SQL file, which maintains consistency across all tables and INSERT statements.

Mappings exist only while the program runs. They are not saved to a reverse-mapping file.

## Research and Design Decisions

### Tokenization

Tokenization replaces sensitive values with tokens and often uses a protected system to maintain the relationship between each token and its original value.

### Pseudonymization

Pseudonymization replaces identifying values with substitutes while retaining useful structure and consistency. This is the primary technique used in this project.

### Synthetic Data

Synthetic data is artificially generated information designed to resemble realistic data. This project uses Faker to generate synthetic PII.

### Selected Approach

The project combines pseudonymization and synthetic data because this approach provides:

* Realistic development and testing values
* Consistency across repeated values
* Consistency across tables
* Preservation of keys and database relationships
* No required reverse-mapping file

SQLGlot was selected instead of regular-expression-based SQL parsing because SQL strings can contain commas, apostrophes, multiline statements, `NULL`, and multiple value tuples. A syntax-tree parser handles these structures more safely.

Column-name classification was selected instead of scanning all strings for PII. This prevents unrelated text fields from being unnecessarily changed.

## Testing

Run the complete automated test suite:

```powershell
python -m pytest
```

Expected result:

```text
56 passed
```

The tests cover:

* Schema discovery
* PII column classification
* Synthetic value generation
* Mapping consistency and uniqueness
* Explicit and implicit column lists
* Single-row and multi-row INSERT statements
* Cross-table consistency
* Apostrophe escaping
* `NULL`, empty, and whitespace-only values
* Preservation of non-sensitive data
* File input and output
* Missing and invalid input paths
* SQL serialization and reparsing
* Seeded reproducibility
* Statement and row-count preservation
* Removal of original PII

## MySQL Validation

The generated `sample_data/anonymized.sql` file was imported into a disposable MySQL 8.4 database.

Validation confirmed:

* Six SQL statements were parsed.
* The `customers`, `orders`, and `shipping` tables were created.
* Each table contained three rows.
* All foreign-key relationships remained valid.
* Customer-to-order identity mismatches: `0`
* Customer-to-shipping identity mismatches: `0`
* Orders without a matching customer: `0`
* Shipments without a matching customer: `0`

These results demonstrate that MySQL can execute the generated file and that the original business relationships remain usable.

## Known Limitations

* Only MySQL input is officially supported.
* Only `INSERT INTO ... VALUES` statements are anonymized.
* `INSERT INTO ... SELECT` is not supported.
* Sensitive columns are identified through recognized column names.
* PII contained inside free-text notes is not detected.
* Only names, addresses, emails, and phone numbers are anonymized.
* `NULL`, empty, and whitespace-only values remain unchanged.
* SQL formatting may change when SQLGlot serializes the syntax tree.
* The application does not provide a reverse-mapping function.

