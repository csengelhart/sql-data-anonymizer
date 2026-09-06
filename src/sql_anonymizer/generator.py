"""Generate realistic synthetic values for supported PII categories."""

from faker import Faker


class SyntheticDataGenerator:
    """Generate synthetic names, addresses, emails, and phone numbers."""

    def __init__(self, seed=None):
        # Use United States formatting for generated data.
        self.fake = Faker("en_US")

        # Seed makes generated values repeatable during testing.
        if seed is not None:
            self.fake.seed_instance(seed)

    def generate_name(self):
        """Generate a synthetic first and last name."""

        first_name = self.fake.first_name()
        last_name = self.fake.last_name()

        return f"{first_name} {last_name}"

    def generate_address(self):
        """Generate a synthetic US mailing address."""

        street = self.fake.street_address()
        city = self.fake.city()
        state = self.fake.state_abbr()
        zip_code = self.fake.zipcode()

        return f"{street}, {city}, {state} {zip_code}"

    def generate_email(self, synthetic_name=None):
        """Generate an email, optionally based on a synthetic name."""

        if synthetic_name is not None:
            email_name = synthetic_name.lower()

            # Remove apostrophes and replace spaces with periods.
            email_name = email_name.replace("'", "")
            email_name = email_name.replace(" ", ".")

            return f"{email_name}@example.com"

        username = self.fake.user_name()

        return f"{username}@example.com"

    def generate_phone(self, original_phone=None):
        """Generate a phone number while preserving common formats."""

        area_code = self.fake.random_int(
            min=200,
            max=999,
        )

        line_number = self.fake.random_int(
            min=1000,
            max=9999,
        )

        # Use 555 as the synthetic central-office code.
        digits = f"{area_code}555{line_number}"

        if original_phone is None:
            return (
                f"{area_code}-555-"
                f"{line_number}"
            )

        # Preserve a format such as (651) 555-9876.
        if original_phone.startswith("("):
            return (
                f"({area_code}) 555-"
                f"{line_number}"
            )

        # Preserve a format such as +1 651-555-9876.
        if original_phone.startswith("+1 "):
            return (
                f"+1 {area_code}-555-"
                f"{line_number}"
            )

        # Preserve a format containing only digits.
        if original_phone.isdigit():
            return digits

        # Use hyphens for all other supported formats.
        return (
            f"{area_code}-555-"
            f"{line_number}"
        )