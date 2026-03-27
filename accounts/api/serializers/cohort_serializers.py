"""
Cohort serializers for accounts API.
Handles cohort CRUD operations with validation and user ownership.
Supports two cohort sources: 'research' (nested filters) and 'search' (flat ES filters).
"""

from rest_framework import serializers

from accounts.models import Cohort
from search.api.serializers.search_serializers import ALLOWED_FILTER_KEYS as SEARCH_FILTER_KEYS

_RESEARCH_FILTER_KEYS = {"visit", "person_demographics", "provider_demographics", "clinical"}

_MAX_ENCOUNTER_IDS = 10_000


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


def _validate_filters_by_source(value: dict, source: str) -> dict:
    """Validate filter keys based on the cohort source."""
    if not isinstance(value, dict):
        raise serializers.ValidationError("Filters must be a JSON object")

    if source == Cohort.SOURCE_SEARCH:
        unknown = set(value.keys()) - SEARCH_FILTER_KEYS
        if unknown:
            raise serializers.ValidationError(
                f"Invalid filter keys for search source: {sorted(unknown)}"
            )
    else:
        unknown = set(value.keys()) - _RESEARCH_FILTER_KEYS
        if unknown:
            raise serializers.ValidationError(
                f"Invalid filter keys for research source: {sorted(unknown)}"
            )
    return value


def _validate_encounter_ids(value):
    """Validate encounter_ids field."""
    if value is None:
        return value
    if not isinstance(value, list):
        raise serializers.ValidationError("encounter_ids must be a list")
    if len(value) > _MAX_ENCOUNTER_IDS:
        raise serializers.ValidationError(f"Too many encounter IDs (max {_MAX_ENCOUNTER_IDS:,}).")
    if not all(isinstance(eid, str) for eid in value):
        raise serializers.ValidationError("All encounter IDs must be strings")
    return value


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
            "source",
            "filters",
            "encounter_ids",
            "search_query",
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
        source = self.initial_data.get("source", Cohort.SOURCE_RESEARCH)
        return _validate_filters_by_source(value, source)

    def validate_encounter_ids(self, value):
        return _validate_encounter_ids(value)


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
            "source",
            "filters",
            "encounter_ids",
            "search_query",
            "visit_count",
        ]

    def validate_visit_count(self, value):
        if value < 0:
            raise serializers.ValidationError("Visit count must be non-negative")
        return value

    def validate_filters(self, value):
        source = self.initial_data.get("source", Cohort.SOURCE_RESEARCH)
        return _validate_filters_by_source(value, source)

    def validate_encounter_ids(self, value):
        return _validate_encounter_ids(value)

    def validate(self, data):
        has_filters = "filters" in data
        has_ids = "encounter_ids" in data and data["encounter_ids"] is not None
        if not has_filters and not has_ids:
            raise serializers.ValidationError("Either filters or encounter_ids must be provided.")
        return data


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
    encounter_id_count = serializers.SerializerMethodField()

    class Meta:
        model = Cohort
        fields = [
            "id",
            "user_id",
            "username",
            "name",
            "description",
            "source",
            "filters",
            "encounter_ids",
            "encounter_id_count",
            "search_query",
            "visit_count",
            "created_at",
            "updated_at",
        ]

    def get_encounter_id_count(self, obj) -> int | None:
        if obj.encounter_ids is not None:
            return len(obj.encounter_ids)
        return None
