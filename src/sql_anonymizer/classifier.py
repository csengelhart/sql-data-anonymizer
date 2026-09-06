"""Identify columns that contain supported types of PII."""


class ColumnClassifier:
    """Classify columns as name, address, email, phone, or non-sensitive."""

    def __init__(self):
        # Common column names used for a person's full name.
        self.name_columns = {
            "name",
            "full_name",
            "customer_name",
            "contact_name",
            "recipient_name",
        }

        # Common column names used for an address.
        self.address_columns = {
            "address",
            "street_address",
            "mailing_address",
            "shipping_address",
            "billing_address",
        }

        # Common column names used for an email address.
        self.email_columns = {
            "email",
            "email_address",
            "contact_email",
        }

        # Common column names used for a phone number.
        self.phone_columns = {
            "phone",
            "phone_number",
            "contact_phone",
            "mobile_phone",
            "telephone",
        }

    def classify(self, column_name):
        """Return the PII category for a column, or None if unsupported."""

        # Make classification case-insensitive.
        column_name = column_name.lower()

        if column_name in self.name_columns:
            return "name"

        if column_name in self.address_columns:
            return "address"

        if column_name in self.email_columns:
            return "email"

        if column_name in self.phone_columns:
            return "phone"

        return None