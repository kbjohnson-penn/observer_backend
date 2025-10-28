"""
Cohort serializers for accounts API.
Handles cohort CRUD operations with validation and user ownership.
"""

from rest_framework import serializers

from accounts.models import Cohort


class CohortSerializer(serializers.ModelSerializer):
    """
    Full serializer for Cohort model.
    Includes all fields for detail views and updates.
    """

    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Cohort
        fields = [
            "id",
            "user_id",
            "username",
            "name",
            "description",
            "filters",
            "visit_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user_id", "username", "created_at", "updated_at"]

    def validate_name(self, value):
        """Validate cohort name is not empty and reasonable length."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Cohort name cannot be empty")
        if len(value) > 255:
            raise serializers.ValidationError("Cohort name too long (max 255 characters)")
        return value.strip()

    def validate_visit_count(self, value):
        """Validate visit count is non-negative."""
        if value < 0:
            raise serializers.ValidationError("Visit count must be non-negative")
        return value

    def validate_filters(self, value):
        """Validate filters is a valid JSON structure."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Filters must be a JSON object")

        # Optional: Validate filter structure matches VisitSearchFilters
        allowed_keys = {"visit", "person_demographics", "provider_demographics", "clinical"}
        if not all(key in allowed_keys for key in value.keys()):
            raise serializers.ValidationError(f"Invalid filter keys. Allowed: {allowed_keys}")

        return value


class CohortCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new cohorts.
    User is automatically set from request.user.
    """

    class Meta:
        model = Cohort
        fields = [
            "name",
            "description",
            "filters",
            "visit_count",
        ]

    def validate_name(self, value):
        """Validate cohort name."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Cohort name cannot be empty")
        if len(value) > 255:
            raise serializers.ValidationError("Cohort name too long (max 255 characters)")
        return value.strip()

    def validate_visit_count(self, value):
        """Validate visit count."""
        if value < 0:
            raise serializers.ValidationError("Visit count must be non-negative")
        return value


class CohortUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing cohorts.
    Only name, description, and filters can be updated.
    """

    class Meta:
        model = Cohort
        fields = ["name", "description", "filters"]

    def validate_name(self, value):
        """Validate cohort name if provided."""
        if value is not None:
            if len(value.strip()) == 0:
                raise serializers.ValidationError("Cohort name cannot be empty")
            if len(value) > 255:
                raise serializers.ValidationError("Cohort name too long (max 255 characters)")
            return value.strip()
        return value


class CohortListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views.
    Excludes heavy fields like detailed filters.
    """

    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    # Computed fields
    filter_summary = serializers.SerializerMethodField()

    class Meta:
        model = Cohort
        fields = [
            "id",
            "user_id",
            "username",
            "name",
            "description",
            "visit_count",
            "filter_summary",
            "created_at",
            "updated_at",
        ]

    def _count_non_empty_filters(self, filter_dict):
        """Helper method to count non-empty filter values."""
        if not filter_dict:
            return 0
        return sum(1 for value in filter_dict.values() if value and value != [] and value != "")

    def get_filter_summary(self, obj):
        """
        Calculate filter summary counts from filters JSON.
        Returns: {visit: 2, person: 3, provider: 1, clinical: 0, total: 6}
        """
        filters = obj.filters
        summary = {
            "visit": self._count_non_empty_filters(filters.get("visit")),
            "person": self._count_non_empty_filters(filters.get("person_demographics")),
            "provider": self._count_non_empty_filters(filters.get("provider_demographics")),
            "clinical": self._count_non_empty_filters(filters.get("clinical")),
        }
        summary["total"] = sum(summary.values())
        return summary
