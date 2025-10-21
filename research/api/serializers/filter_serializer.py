from rest_framework import serializers


class FilterSerializer(serializers.Serializer):
    """
    Serializer for validating filter parameters in search endpoints.

    Prevents DoS attacks via excessive filters and validates filter structure.
    """
    filters = serializers.JSONField(required=False, default=dict)
    sort = serializers.JSONField(required=False, default=dict)

    # Allowed filter keys for visit search
    ALLOWED_FILTER_KEYS = {
        'age_from', 'age_to', 'gender', 'race', 'ethnicity',
        'tier_id', 'visit_start_date_from', 'visit_start_date_to',
        'visit_source_value', 'provider_gender', 'provider_race',
        'provider_ethnicity', 'year_of_birth_from', 'year_of_birth_to'
    }

    # Allowed sort keys
    ALLOWED_SORT_KEYS = {
        'visit_start_date', 'tier_id', 'year_of_birth'
    }

    # Maximum number of filters to prevent DoS
    MAX_FILTER_COUNT = 50

    def validate_filters(self, value):
        """
        Validate filter dictionary structure and keys.
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("Filters must be a dictionary")

        # Validate max filter count to prevent DoS
        if len(value) > self.MAX_FILTER_COUNT:
            raise serializers.ValidationError(
                f"Too many filters (max {self.MAX_FILTER_COUNT})"
            )

        # Validate filter keys are allowed
        invalid_keys = set(value.keys()) - self.ALLOWED_FILTER_KEYS
        if invalid_keys:
            raise serializers.ValidationError(
                f"Invalid filter keys: {', '.join(invalid_keys)}"
            )

        # Validate age range values
        age_from = value.get('age_from')
        age_to = value.get('age_to')

        if age_from is not None:
            try:
                age_from_val = int(age_from)
                if age_from_val < 0 or age_from_val > 150:
                    raise serializers.ValidationError(
                        "age_from must be between 0 and 150"
                    )
            except (ValueError, TypeError):
                raise serializers.ValidationError("age_from must be a valid integer")

        if age_to is not None:
            try:
                age_to_val = int(age_to)
                if age_to_val < 0 or age_to_val > 150:
                    raise serializers.ValidationError(
                        "age_to must be between 0 and 150"
                    )
            except (ValueError, TypeError):
                raise serializers.ValidationError("age_to must be a valid integer")

        # Validate logical consistency
        if age_from is not None and age_to is not None:
            if int(age_from) > int(age_to):
                raise serializers.ValidationError(
                    "age_from cannot be greater than age_to"
                )

        # Validate year of birth range
        year_from = value.get('year_of_birth_from')
        year_to = value.get('year_of_birth_to')

        if year_from is not None and year_to is not None:
            try:
                if int(year_from) > int(year_to):
                    raise serializers.ValidationError(
                        "year_of_birth_from cannot be greater than year_of_birth_to"
                    )
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    "year_of_birth values must be valid integers"
                )

        # Validate tier_id
        tier_id = value.get('tier_id')
        if tier_id is not None:
            try:
                tier_id_val = int(tier_id)
                if tier_id_val < 1 or tier_id_val > 5:
                    raise serializers.ValidationError(
                        "tier_id must be between 1 and 5"
                    )
            except (ValueError, TypeError):
                raise serializers.ValidationError("tier_id must be a valid integer")

        return value

    def validate_sort(self, value):
        """
        Validate sort dictionary structure and keys.
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("Sort must be a dictionary")

        # Validate sort keys are allowed
        invalid_keys = set(value.keys()) - self.ALLOWED_SORT_KEYS
        if invalid_keys:
            raise serializers.ValidationError(
                f"Invalid sort keys: {', '.join(invalid_keys)}"
            )

        # Validate sort order values
        for key, order in value.items():
            if order not in ['asc', 'desc', 'ASC', 'DESC']:
                raise serializers.ValidationError(
                    f"Invalid sort order for '{key}': must be 'asc' or 'desc'"
                )

        return value
