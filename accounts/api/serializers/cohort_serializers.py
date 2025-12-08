"""
Cohort serializers for accounts API.
Handles cohort CRUD operations with validation and user ownership.
"""

from rest_framework import serializers

from accounts.models import Cohort


class CohortNameValidationMixin:
    """
    Mixin providing cohort name validation logic.
    Reusable across multiple serializers to avoid code duplication.
    """

    def validate_name(self, value):
        """Validate cohort name is not empty and reasonable length."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Cohort name cannot be empty")
        if len(value) > 255:
            raise serializers.ValidationError("Cohort name too long (max 255 characters)")
        return value.strip()


class CohortSerializer(CohortNameValidationMixin, serializers.ModelSerializer):
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


class CohortCreateSerializer(CohortNameValidationMixin, serializers.ModelSerializer):
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

    def validate_visit_count(self, value):
        """Validate visit count."""
        if value < 0:
            raise serializers.ValidationError("Visit count must be non-negative")
        return value


class CohortUpdateSerializer(CohortNameValidationMixin, serializers.ModelSerializer):
    """
    Serializer for updating existing cohorts.
    Only name, description, and filters can be updated.
    """

    class Meta:
        model = Cohort
        fields = ["name", "description", "filters"]


class CohortListSerializer(serializers.ModelSerializer):
    """
    Serializer for list views.
    Includes filters for display in cohort cards.
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
