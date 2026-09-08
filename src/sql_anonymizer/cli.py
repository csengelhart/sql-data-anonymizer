"""Provide the command-line interface for the SQL anonymizer."""

import argparse

from sql_anonymizer.anonymizer import anonymize_file


def create_argument_parser():
    """Create and configure the command-line argument parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Replace names, addresses, emails, and phone numbers "
            "in a MySQL file with realistic synthetic values."
        )
    )

    parser.add_argument(
        "input_file",
        help="Path to the original MySQL file.",
    )

    parser.add_argument(
        "output_file",
        help="Path for the anonymized MySQL file.",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional number used for repeatable synthetic data.",
    )

    return parser


def main():
    """Run the SQL anonymizer from the command line."""

    parser = create_argument_parser()
    arguments = parser.parse_args()

    try:
        insert_count = anonymize_file(
            arguments.input_file,
            arguments.output_file,
            arguments.seed,
        )

    except (
        FileNotFoundError,
        PermissionError,
        ValueError,
        KeyError,
    ) as error:
        parser.exit(
            status=1,
            message=f"Error: {error}\n",
        )

    print(
        f"Anonymization complete. "
        f"Processed {insert_count} INSERT statements."
    )

    print(
        f"Output written to: {arguments.output_file}"
    )


if __name__ == "__main__":
    main()