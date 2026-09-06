"""Tests for sensitive-column classification."""

from sql_anonymizer.classifier import ColumnClassifier


def test_name_columns_are_classified():
    """Common name columns should be classified as names."""

    classifier = ColumnClassifier()

    assert classifier.classify("name") == "name"
    assert classifier.classify("full_name") == "name"
    assert classifier.classify("customer_name") == "name"
    assert classifier.classify("contact_name") == "name"
    assert classifier.classify("recipient_name") == "name"


def test_address_columns_are_classified():
    """Common address columns should be classified as addresses."""

    classifier = ColumnClassifier()

    assert classifier.classify("address") == "address"
    assert classifier.classify("street_address") == "address"
    assert classifier.classify("mailing_address") == "address"
    assert classifier.classify("shipping_address") == "address"
    assert classifier.classify("billing_address") == "address"


def test_email_columns_are_classified():
    """Common email columns should be classified as email addresses."""

    classifier = ColumnClassifier()

    assert classifier.classify("email") == "email"
    assert classifier.classify("email_address") == "email"
    assert classifier.classify("contact_email") == "email"


def test_phone_columns_are_classified():
    """Common phone columns should be classified as phone numbers."""

    classifier = ColumnClassifier()

    assert classifier.classify("phone") == "phone"
    assert classifier.classify("phone_number") == "phone"
    assert classifier.classify("contact_phone") == "phone"
    assert classifier.classify("mobile_phone") == "phone"
    assert classifier.classify("telephone") == "phone"


def test_classification_is_case_insensitive():
    """Capitalization should not affect column classification."""

    classifier = ColumnClassifier()

    assert classifier.classify("FULL_NAME") == "name"
    assert classifier.classify("Shipping_Address") == "address"
    assert classifier.classify("CONTACT_EMAIL") == "email"
    assert classifier.classify("Phone") == "phone"


def test_non_sensitive_columns_return_none():
    """Columns outside the four supported categories should return None."""

    classifier = ColumnClassifier()

    assert classifier.classify("customer_id") is None
    assert classifier.classify("account_status") is None
    assert classifier.classify("order_total") is None
    assert classifier.classify("order_date") is None
    assert classifier.classify("delivery_instructions") is None


def test_similar_column_names_are_not_false_matches():
    """A partial word match should not automatically identify PII."""

    classifier = ColumnClassifier()

    assert classifier.classify("username") is None
    assert classifier.classify("email_status") is None
    assert classifier.classify("phone_extension_enabled") is None