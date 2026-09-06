"""Tests for synthetic PII generation."""

from sql_anonymizer.generator import SyntheticDataGenerator


def test_generate_name():
    """A generated name should contain a first and last name."""

    generator = SyntheticDataGenerator(seed=499)

    name = generator.generate_name()

    assert isinstance(name, str)
    assert len(name) > 0
    assert " " in name


def test_generate_address():
    """A generated address should resemble a one-line US address."""

    generator = SyntheticDataGenerator(seed=499)

    address = generator.generate_address()

    assert isinstance(address, str)
    assert len(address) > 0
    assert "," in address
    assert "\n" not in address


def test_generate_email_from_name():
    """An email should correspond to the supplied synthetic name."""

    generator = SyntheticDataGenerator(seed=499)

    email = generator.generate_email("Michael Anderson")

    assert email == "michael.anderson@example.com"


def test_generate_email_removes_apostrophe():
    """Apostrophes should not remain in a generated email username."""

    generator = SyntheticDataGenerator(seed=499)

    email = generator.generate_email("Sarah O'Brien")

    assert email == "sarah.obrien@example.com"


def test_generate_email_without_name():
    """An email can be generated when no name is available."""

    generator = SyntheticDataGenerator(seed=499)

    email = generator.generate_email()

    assert email.endswith("@example.com")
    assert " " not in email


def test_phone_format_with_hyphens():
    """A hyphenated phone should retain its formatting style."""

    generator = SyntheticDataGenerator(seed=499)

    phone = generator.generate_phone("612-555-1234")

    parts = phone.split("-")

    assert len(parts) == 3
    assert len(parts[0]) == 3
    assert parts[1] == "555"
    assert len(parts[2]) == 4
    assert phone != "612-555-1234"


def test_phone_format_with_parentheses():
    """A phone with parentheses should retain its formatting style."""

    generator = SyntheticDataGenerator(seed=499)

    phone = generator.generate_phone("(651) 555-9876")

    assert phone.startswith("(")
    assert ") 555-" in phone
    assert phone != "(651) 555-9876"


def test_phone_format_with_digits_only():
    """A digits-only phone should remain digits-only."""

    generator = SyntheticDataGenerator(seed=499)

    phone = generator.generate_phone("6125551234")

    assert phone.isdigit()
    assert len(phone) == 10
    assert phone != "6125551234"


def test_seed_produces_repeatable_values():
    """The same seed should produce the same sequence of values."""

    first_generator = SyntheticDataGenerator(seed=499)
    second_generator = SyntheticDataGenerator(seed=499)

    first_name = first_generator.generate_name()
    second_name = second_generator.generate_name()

    assert first_name == second_name