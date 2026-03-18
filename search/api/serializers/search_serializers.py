"""
Serializers for the Observer search API.
"""

import re

from django.conf import settings

from rest_framework import serializers

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

ALLOWED_FILTER_KEYS = {
    "department",
    "date_from",
    "date_to",
    "icd_codes",
    "cpt_codes",
    "drug_names",
    "note_types",
    "patient_gender",
    "patient_race",
    "patient_ethnicity",
    "provider_gender",
    "provider_race",
    "provider_ethnicity",
    "has_transcript",
    "has_audio",
    "has_provider_view",
    "has_patient_view",
    "has_room_view",
    "has_notes",
}


class SearchRequestSerializer(serializers.Serializer):
    query = serializers.CharField(
        max_length=500,
        allow_blank=True,
        default="",
        trim_whitespace=True,
    )
    filters = serializers.DictField(
        child=serializers.JSONField(),
        required=False,
        default=dict,
    )
    page = serializers.IntegerField(min_value=1, max_value=100, default=1)
    page_size = serializers.IntegerField(min_value=1, max_value=100, default=20)
    sort = serializers.DictField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
        default=None,
    )
    search_type = serializers.ChoiceField(
        choices=["keyword", "semantic"],
        default="keyword",
    )

    def validate_query(self, value: str) -> str:
        return value.strip()

    def validate_filters(self, value: dict) -> dict:
        unknown = set(value.keys()) - ALLOWED_FILTER_KEYS
        if unknown:
            raise serializers.ValidationError(f"Unknown filter keys: {sorted(unknown)}")
        if len(value) > 50:
            raise serializers.ValidationError("Too many filter keys (max 50).")

        self._validate_date_filters(value)
        self._validate_list_filters(value)
        self._validate_bool_filters(value)
        return value

    @staticmethod
    def _validate_date_filters(value: dict) -> None:
        for field in ("date_from", "date_to"):
            if field in value and value[field] is not None:
                if not _DATE_RE.match(str(value[field])):
                    raise serializers.ValidationError(f"'{field}' must be in YYYY-MM-DD format.")

    @staticmethod
    def _validate_list_filters(value: dict) -> None:
        list_fields = {
            "department",
            "icd_codes",
            "cpt_codes",
            "drug_names",
            "note_types",
            "patient_gender",
            "patient_race",
            "patient_ethnicity",
            "provider_gender",
            "provider_race",
            "provider_ethnicity",
        }
        for field in list_fields:
            if field in value and value[field] is not None:
                if not isinstance(value[field], list):
                    raise serializers.ValidationError(f"'{field}' must be a list.")
                if not all(isinstance(v, str) for v in value[field]):
                    raise serializers.ValidationError(f"'{field}' must be a list of strings.")

    @staticmethod
    def _validate_bool_filters(value: dict) -> None:
        bool_fields = {
            "has_transcript",
            "has_audio",
            "has_provider_view",
            "has_patient_view",
            "has_room_view",
            "has_notes",
        }
        for field in bool_fields:
            if field in value and value[field] is not None:
                if not isinstance(value[field], bool):
                    raise serializers.ValidationError(f"'{field}' must be a boolean.")

    def validate_sort(self, value: dict | None) -> dict | None:
        if value is None:
            return None
        allowed = {"visit_date", "_score", "tier_level"}
        unknown = set(value.keys()) - allowed
        if unknown:
            raise serializers.ValidationError(
                f"Unknown sort fields: {sorted(unknown)}. Allowed: {sorted(allowed)}"
            )
        for field, direction in value.items():
            if direction not in ("asc", "desc"):
                raise serializers.ValidationError(
                    f"Sort direction for '{field}' must be 'asc' or 'desc'."
                )
        return value

    def validate_search_type(self, value: str) -> str:
        if value == "semantic" and not settings.SEARCH_FEATURES.get("semantic_enabled"):
            raise serializers.ValidationError("Semantic search is not enabled in this environment.")
        return value
