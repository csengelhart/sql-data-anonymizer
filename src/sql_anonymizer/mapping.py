"""Maintain consistent mappings between original and synthetic values."""


class MappingRegistry:
    """Store anonymized replacements for each supported PII category."""

    def __init__(self):
        # Each PII category has its own mapping dictionary.
        #
        # Example:
        # {
        #     "name": {
        #         "John Smith": "Michael Anderson"
        #     },
        #     "email": {
        #         "john@gmail.com": "michael@example.com"
        #     }
        # }
        self.mappings = {
            "name": {},
            "address": {},
            "email": {},
            "phone": {},
        }

        # These sets prevent two different original values from receiving
        # the same synthetic replacement.
        self.used_values = {
            "name": set(),
            "address": set(),
            "email": set(),
            "phone": set(),
        }

    def get_or_create(self, category, original_value, generator):
        """Return an existing replacement or generate a new one."""

        if category not in self.mappings:
            raise ValueError(
                f"Unsupported PII category: '{category}'."
            )

        category_mappings = self.mappings[category]

        # Return the existing replacement when the value has been seen before.
        if original_value in category_mappings:
            return category_mappings[original_value]

        # Generate a replacement for a value that has not been seen before.
        replacement = generator()

        # Generate another value if the replacement is already being used.
        attempts = 1

        while replacement in self.used_values[category]:
            if attempts >= 100:
                raise RuntimeError(
                    f"Could not generate a unique {category} replacement."
                )

            replacement = generator()
            attempts += 1

        # Store the relationship for future occurrences.
        category_mappings[original_value] = replacement
        self.used_values[category].add(replacement)

        return replacement

    def get_mapping(self, category):
        """Return the mappings stored for one PII category."""

        if category not in self.mappings:
            raise ValueError(
                f"Unsupported PII category: '{category}'."
            )

        return self.mappings[category].copy()