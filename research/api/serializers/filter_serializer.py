from rest_framework import serializers


class FilterSerializer(serializers.Serializer):
    """
    Serializer for validating filter parameters in search endpoints.

    Prevents DoS attacks via excessive filters and validates nested filter structure.
    Supports both flat filters (legacy) and nested filters (current).

    Expected structure:
    {
        "filters": {
            "visit": {...},
            "person_demographics": {...},
            "provider_demographics": {...},
            "clinical": {...}
        },
        "sort": {
            "field": "id",
            "direction": "asc"
        }
    }
    """

    filters = serializers.JSONField(required=False, default=dict)
    sort = serializers.JSONField(required=False, default=dict)

    # Allowed top-level filter categories (nested structure)
    ALLOWED_FILTER_CATEGORIES = {
        "visit",
        "person_demographics",
        "provider_demographics",
        "clinical",
    }

    # Allowed flat filter keys (legacy support - for backward compatibility)
    ALLOWED_FLAT_FILTER_KEYS = {
        "age_from",
        "age_to",
        "gender",
        "race",
        "ethnicity",
        "tier_id",
        "visit_start_date_from",
        "visit_start_date_to",
        "visit_source_value",
        "provider_gender",
        "provider_race",
        "provider_ethnicity",
        "year_of_birth_from",
        "year_of_birth_to",
    }

    # Allowed sort keys (new structure: field + direction)
    ALLOWED_SORT_KEYS = {"field", "direction"}

    # Allowed sort field values
    ALLOWED_SORT_FIELDS = {
        "id",
        "visit_start_date",
        "tier_id",
        "person_id",
        "provider_id",
        "visit_source_value",
        "year_of_birth",
    }

    # Maximum number of filters to prevent DoS
    MAX_FILTER_COUNT = 50

    def validate_filters(self, value):
        """
        Validate filter dictionary structure and keys.
        Supports both nested (current) and flat (legacy) filter structures.
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("Filters must be a dictionary")

        # Empty filters are valid
        if not value:
            return value

        # Validate max filter count to prevent DoS (count all nested filters)
        total_filters = self._count_nested_filters(value)
        if total_filters > self.MAX_FILTER_COUNT:
            raise serializers.ValidationError(f"Too many filters (max {self.MAX_FILTER_COUNT})")

        # Check if using nested structure (preferred) or flat structure (legacy)
        is_nested = any(key in self.ALLOWED_FILTER_CATEGORIES for key in value.keys())
        is_flat = any(key in self.ALLOWED_FLAT_FILTER_KEYS for key in value.keys())

        if is_nested:
            # Validate nested structure
            invalid_categories = set(value.keys()) - self.ALLOWED_FILTER_CATEGORIES
            if invalid_categories:
                raise serializers.ValidationError(
                    f"Invalid filter categories: {', '.join(invalid_categories)}. "
                    f"Allowed: {', '.join(self.ALLOWED_FILTER_CATEGORIES)}"
                )

            # Validate each category is a dict
            for category, filters in value.items():
                if filters is not None and not isinstance(filters, dict):
                    raise serializers.ValidationError(
                        f"Filter category '{category}' must be a dictionary"
                    )

            # Validate tier_id if present in visit filters
            visit_filters = value.get("visit", {})
            if visit_filters:
                self._validate_tier_id(visit_filters.get("tier_id"))

            # Validate year of birth ranges if present
            person_demo = value.get("person_demographics", {})
            if person_demo:
                self._validate_year_of_birth_range(
                    person_demo.get("year_of_birth_from"), person_demo.get("year_of_birth_to")
                )
                # Validate demographic filter values
                self._validate_demographic_values(person_demo.get("gender"), "gender")
                self._validate_demographic_values(person_demo.get("race"), "race")
                self._validate_demographic_values(person_demo.get("ethnicity"), "ethnicity")

            provider_demo = value.get("provider_demographics", {})
            if provider_demo:
                self._validate_year_of_birth_range(
                    provider_demo.get("year_of_birth_from"), provider_demo.get("year_of_birth_to")
                )
                # Validate demographic filter values
                self._validate_demographic_values(provider_demo.get("gender"), "gender")
                self._validate_demographic_values(provider_demo.get("race"), "race")
                self._validate_demographic_values(provider_demo.get("ethnicity"), "ethnicity")

        elif is_flat:
            # Validate flat structure (legacy support)
            invalid_keys = set(value.keys()) - self.ALLOWED_FLAT_FILTER_KEYS
            if invalid_keys:
                raise serializers.ValidationError(f"Invalid filter keys: {', '.join(invalid_keys)}")

            # Validate tier_id for flat structure
            self._validate_tier_id(value.get("tier_id"))

            # Validate year of birth range for flat structure
            self._validate_year_of_birth_range(
                value.get("year_of_birth_from"), value.get("year_of_birth_to")
            )

        return value

    def _validate_demographic_values(self, values, field_name):
        """
        Validate demographic filter values.
        Ensures values are strings and documents that NULL_MARKER is accepted.

        Args:
            values: List of filter values (may include NULL_MARKER for NULL matching)
            field_name: Name of the field for error messages
        """
        if values is None:
            return

        if not isinstance(values, list):
            raise serializers.ValidationError(f"{field_name} must be a list")

        for value in values:
            if not isinstance(value, str):
                raise serializers.ValidationError(f"{field_name} values must be strings")
            # NULL_MARKER is a reserved marker for filtering NULL database values
            # Other string values will be matched directly against the database

    def _count_nested_filters(self, filters, depth=0):
        """
        Recursively count all filters in nested structure.
        Prevents DoS attacks via excessive filter counts.
        """
        if depth > 5:  # Prevent infinite recursion
            raise serializers.ValidationError("Filter nesting too deep (max 5 levels)")

        count = 0
        for key, value in filters.items():
            if isinstance(value, dict):
                count += self._count_nested_filters(value, depth + 1)
            elif value is not None and value != [] and value != "":
                count += 1

        return count

    def _validate_tier_id(self, tier_id):
        """
        Validate tier_id value(s).
        Can be a single integer or a list of integers.
        """
        if tier_id is None:
            return

        if isinstance(tier_id, list):
            # Validate each tier ID in list
            for tid in tier_id:
                try:
                    tid_val = int(tid)
                    if tid_val < 1 or tid_val > 5:
                        raise serializers.ValidationError("tier_id values must be between 1 and 5")
                except (ValueError, TypeError):
                    raise serializers.ValidationError("tier_id values must be valid integers")
        else:
            # Single tier ID
            try:
                tier_id_val = int(tier_id)
                if tier_id_val < 1 or tier_id_val > 5:
                    raise serializers.ValidationError("tier_id must be between 1 and 5")
            except (ValueError, TypeError):
                raise serializers.ValidationError("tier_id must be a valid integer")

    def _validate_year_of_birth_range(self, year_from, year_to):
        """
        Validate year of birth range values.
        """
        if year_from is not None and year_to is not None:
            try:
                year_from_val = int(year_from)
                year_to_val = int(year_to)

                if year_from_val > year_to_val:
                    raise serializers.ValidationError(
                        "year_of_birth_from cannot be greater than year_of_birth_to"
                    )

                # Validate reasonable year range (1900 to current year + 1)
                from datetime import datetime

                current_year = datetime.now().year
                if year_from_val < 1900 or year_from_val > current_year + 1:
                    raise serializers.ValidationError(
                        f"year_of_birth_from must be between 1900 and {current_year + 1}"
                    )
                if year_to_val < 1900 or year_to_val > current_year + 1:
                    raise serializers.ValidationError(
                        f"year_of_birth_to must be between 1900 and {current_year + 1}"
                    )

            except (ValueError, TypeError):
                raise serializers.ValidationError("year_of_birth values must be valid integers")

    def validate_sort(self, value):
        """
        Validate sort dictionary structure and keys.
        Expects format: {"field": "id", "direction": "asc"}
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("Sort must be a dictionary")

        # Empty sort is valid (will use default sorting)
        if not value:
            return value

        # Validate sort keys are allowed
        invalid_keys = set(value.keys()) - self.ALLOWED_SORT_KEYS
        if invalid_keys:
            raise serializers.ValidationError(
                f"Invalid sort keys: {', '.join(invalid_keys)}. "
                f"Allowed: {', '.join(self.ALLOWED_SORT_KEYS)}"
            )

        # Validate field value if present
        field = value.get("field")
        if field and field not in self.ALLOWED_SORT_FIELDS:
            raise serializers.ValidationError(
                f"Invalid sort field: '{field}'. " f"Allowed: {', '.join(self.ALLOWED_SORT_FIELDS)}"
            )

        # Validate direction value if present
        direction = value.get("direction")
        if direction and direction not in ["asc", "desc", "ASC", "DESC"]:
            raise serializers.ValidationError(
                f"Invalid sort direction: must be 'asc' or 'desc', got '{direction}'"
            )

        return value
