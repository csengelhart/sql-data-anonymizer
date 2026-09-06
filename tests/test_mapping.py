"""Tests for consistent anonymization mappings."""

import pytest

from sql_anonymizer.mapping import MappingRegistry


def test_new_value_receives_generated_replacement():
    """A new original value should receive a generated replacement."""

    registry = MappingRegistry()

    def generate_name():
        return "Michael Anderson"

    replacement = registry.get_or_create(
        "name",
        "John Smith",
        generate_name,
    )

    assert replacement == "Michael Anderson"


def test_repeated_value_receives_same_replacement():
    """A repeated original value should reuse its first replacement."""

    registry = MappingRegistry()

    generated_names = iter([
        "Michael Anderson",
        "Sarah Johnson",
    ])

    def generate_name():
        return next(generated_names)

    first_replacement = registry.get_or_create(
        "name",
        "John Smith",
        generate_name,
    )

    second_replacement = registry.get_or_create(
        "name",
        "John Smith",
        generate_name,
    )

    assert first_replacement == "Michael Anderson"
    assert second_replacement == "Michael Anderson"


def test_different_original_values_receive_unique_replacements():
    """Different originals should not share a synthetic value."""

    registry = MappingRegistry()

    generated_names = iter([
        "Michael Anderson",
        "Michael Anderson",
        "Sarah Johnson",
    ])

    def generate_name():
        return next(generated_names)

    first_replacement = registry.get_or_create(
        "name",
        "John Smith",
        generate_name,
    )

    second_replacement = registry.get_or_create(
        "name",
        "Jane Doe",
        generate_name,
    )

    assert first_replacement == "Michael Anderson"
    assert second_replacement == "Sarah Johnson"


def test_categories_have_separate_mappings():
    """The same original text may have different category mappings."""

    registry = MappingRegistry()

    def generate_name():
        return "Jordan Davis"

    def generate_address():
        return "500 Oak Street"

    name_replacement = registry.get_or_create(
        "name",
        "Jordan",
        generate_name,
    )

    address_replacement = registry.get_or_create(
        "address",
        "Jordan",
        generate_address,
    )

    assert name_replacement == "Jordan Davis"
    assert address_replacement == "500 Oak Street"


def test_get_mapping_returns_stored_values():
    """The registry should provide its stored mappings for validation."""

    registry = MappingRegistry()

    def generate_email():
        return "michael.anderson@example.com"

    registry.get_or_create(
        "email",
        "john.smith@gmail.com",
        generate_email,
    )

    email_mappings = registry.get_mapping("email")

    assert email_mappings == {
        "john.smith@gmail.com": "michael.anderson@example.com"
    }


def test_get_mapping_returns_a_copy():
    """Changing a returned dictionary should not change the registry."""

    registry = MappingRegistry()

    def generate_phone():
        return "763-555-8472"

    registry.get_or_create(
        "phone",
        "612-555-1234",
        generate_phone,
    )

    returned_mapping = registry.get_mapping("phone")
    returned_mapping["612-555-1234"] = "changed"

    actual_mapping = registry.get_mapping("phone")

    assert actual_mapping["612-555-1234"] == "763-555-8472"


def test_unsupported_category_raises_error():
    """An unsupported PII category should raise a clear error."""

    registry = MappingRegistry()

    def generate_value():
        return "Synthetic Value"

    with pytest.raises(
        ValueError,
        match="Unsupported PII category",
    ):
        registry.get_or_create(
            "social_security_number",
            "123-45-6789",
            generate_value,
        )