"""
Cohort Data ViewSet for fetching all OMOP table data filtered by cohort criteria.
Returns data in SampleDataAPIResponse format for HealthcareDataBrowser component.

Supports three cohort retrieval modes:
1. encounter_ids — explicit list of visit IDs (hand-picked from search)
2. source="search" — flat EncounterSearchFilters mapped to ORM queries
3. source="research" — nested VisitSearchFilters via VisitSearchViewSet
"""

from django.db.models import Q, QuerySet

from rest_framework import status
from rest_framework.response import Response

from accounts.models import Cohort
from research.models import (
    AuditLogs,
    ConditionOccurrence,
    DrugExposure,
    Measurement,
    Note,
    Observation,
    PatientSurvey,
    Person,
    ProcedureOccurrence,
    Provider,
    ProviderSurvey,
    VisitOccurrence,
)
from shared.api.permissions import BaseAuthenticatedViewSet, filter_queryset_by_user_tier
from shared.constants import MAX_COHORT_DATA_VISITS


class CohortDataViewSet(BaseAuthenticatedViewSet):
    """
    ViewSet for fetching all OMOP table data filtered by a cohort's saved filters.
    Inherits authentication and permissions from BaseAuthenticatedViewSet.
    Only supports retrieve method (GET /cohorts/{id}/data/).

    Returns data structure matching SampleDataAPIResponse for HealthcareDataBrowser.
    """

    def retrieve(self, request, pk=None):
        """
        GET endpoint to fetch all OMOP data for a specific cohort.

        Args:
            request: HTTP request object
            pk: Cohort ID

        Returns:
            Response with all OMOP tables filtered by cohort criteria

        Security:
            - Requires authentication (inherited from BaseAuthenticatedViewSet)
            - Verifies user owns the cohort
            - Applies tier-based access control to visits
        """
        try:
            # 1. Get cohort from accounts database
            cohort = Cohort.objects.using("accounts").get(pk=pk)

            # 2. Security: Verify user owns this cohort
            if cohort.user_id != request.user.id:
                return Response(
                    {"detail": "You do not have permission to view this cohort."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # 3. Get filtered visits — branch on cohort type
            queryset = self._get_base_queryset(request.user)
            if cohort.encounter_ids:
                int_ids = [int(eid) for eid in cohort.encounter_ids]
                queryset = queryset.filter(id__in=int_ids)
            elif cohort.source == Cohort.SOURCE_SEARCH:
                queryset = self._apply_search_filters(queryset, cohort.filters or {})
            else:
                queryset = self._apply_filters(queryset, cohort.filters or {})

            # 4. Guard against loading too much data into memory
            visit_count = queryset.count()
            if visit_count > MAX_COHORT_DATA_VISITS:
                return Response(
                    {
                        "detail": (
                            f"Cohort contains {visit_count:,} visits, which exceeds "
                            f"the maximum of {MAX_COHORT_DATA_VISITS:,}. "
                            "Please refine your cohort filters."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get all visits as list of dicts
            visits = list(queryset.values())

            # 4. Extract IDs for related table queries
            visit_ids = [v["id"] for v in visits]
            person_ids = list(set([v["person_id"] for v in visits]))
            provider_ids = list(set([v["provider_id"] for v in visits]))

            # 5. Query all OMOP tables using .values() for raw data
            response_data = {
                "persons": list(
                    Person.objects.using("research").filter(id__in=person_ids).values()
                ),
                "providers": list(
                    Provider.objects.using("research").filter(id__in=provider_ids).values()
                ),
                "visits": visits,
                "notes": list(
                    Note.objects.using("research")
                    .filter(visit_occurrence_id__in=visit_ids)
                    .values()
                ),
                "conditions": list(
                    ConditionOccurrence.objects.using("research")
                    .filter(visit_occurrence_id__in=visit_ids)
                    .values()
                ),
                "drugs": list(
                    DrugExposure.objects.using("research")
                    .filter(visit_occurrence_id__in=visit_ids)
                    .values()
                ),
                "procedures": list(
                    ProcedureOccurrence.objects.using("research")
                    .filter(visit_occurrence_id__in=visit_ids)
                    .values()
                ),
                "measurements": list(
                    Measurement.objects.using("research")
                    .filter(visit_occurrence_id__in=visit_ids)
                    .values()
                ),
                "observations": list(
                    Observation.objects.using("research")
                    .filter(visit_occurrence_id__in=visit_ids)
                    .values()
                ),
                "patient_surveys": list(
                    PatientSurvey.objects.using("research")
                    .filter(visit_occurrence_id__in=visit_ids)
                    .values()
                ),
                "provider_surveys": list(
                    ProviderSurvey.objects.using("research")
                    .filter(visit_occurrence_id__in=visit_ids)
                    .values()
                ),
                "audit_logs": list(
                    AuditLogs.objects.using("research")
                    .filter(visit_occurrence_id__in=visit_ids)
                    .values()
                ),
                "concepts": [],  # Empty for now, can be populated if needed
                "_metadata": {
                    "description": f"Cohort: {cohort.name}",
                    "source": "cohort_filter",
                    "count": {
                        "visits": len(visit_ids),
                        "persons": len(person_ids),
                        "providers": len(provider_ids),
                    },
                },
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Cohort.DoesNotExist:
            return Response(
                {"detail": f"Cohort with ID {pk} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception:
            # Log the error for debugging
            return Response(
                {"detail": "Error fetching cohort data."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_base_queryset(self, user):
        """
        Get base queryset filtered by user's tier access.
        Includes person and provider data for demographics.
        """
        return filter_queryset_by_user_tier(
            VisitOccurrence.objects.using("research").select_related("person", "provider").all(),
            user,
            related_field="tier_level",
        )

    def _apply_filters(self, queryset, filters):
        """
        Apply legacy *research* cohort filters (nested VisitSearchFilters).
        Delegates to VisitSearchViewSet filter methods.
        """
        from research.api.viewsets.private.visit_search_viewset import VisitSearchViewSet

        vs = VisitSearchViewSet()
        queryset = vs._apply_visit_filters(queryset, filters.get("visit", {}))
        queryset = vs._apply_person_demographic_filters(
            queryset, filters.get("person_demographics", {})
        )
        queryset = vs._apply_provider_demographic_filters(
            queryset, filters.get("provider_demographics", {})
        )
        queryset = vs._apply_clinical_filters(queryset, filters.get("clinical", {}))
        return queryset

    @staticmethod
    def _apply_search_filters(queryset: QuerySet, filters: dict) -> QuerySet:
        """
        Apply flat *search* cohort filters (EncounterSearchFilters) to an ORM queryset.
        """
        queryset = _apply_search_date_and_dept(queryset, filters)
        queryset = _apply_search_demographics(queryset, filters)
        queryset = _apply_search_clinical(queryset, filters)
        queryset = _apply_search_boolean_flags(queryset, filters)
        return queryset


# ---------------------------------------------------------------------------
# Helpers for _apply_search_filters (split to keep cyclomatic complexity low)
# ---------------------------------------------------------------------------

_DEMOGRAPHIC_FIELDS: list[tuple[str, str]] = [
    ("patient_gender", "person__gender_source_value__in"),
    ("patient_race", "person__race_source_value__in"),
    ("patient_ethnicity", "person__ethnicity_source_value__in"),
    ("provider_gender", "provider__gender_source_value__in"),
    ("provider_race", "provider__race_source_value__in"),
    ("provider_ethnicity", "provider__ethnicity_source_value__in"),
]

_FLAG_TO_FILE_TYPE: dict[str, str] = {
    "has_transcript": "transcript",
    "has_audio": "audio",
    "has_provider_view": "provider_view",
    "has_patient_view": "patient_view",
    "has_room_view": "room_view",
}


def _apply_search_date_and_dept(qs: QuerySet, f: dict) -> QuerySet:
    if f.get("date_from"):
        qs = qs.filter(visit_start_date__gte=f["date_from"])
    if f.get("date_to"):
        qs = qs.filter(visit_start_date__lte=f["date_to"])
    if f.get("department"):
        qs = qs.filter(department__in=f["department"])
    return qs


def _apply_search_demographics(qs: QuerySet, f: dict) -> QuerySet:
    for key, lookup in _DEMOGRAPHIC_FIELDS:
        if f.get(key):
            qs = qs.filter(**{lookup: f[key]})
    return qs


def _apply_search_clinical(qs: QuerySet, f: dict) -> QuerySet:
    if f.get("icd_codes"):
        qs = qs.filter(conditionoccurrence__condition_source_value__in=f["icd_codes"]).distinct()
    if f.get("cpt_codes"):
        qs = qs.filter(procedureoccurrence__name__in=f["cpt_codes"]).distinct()
    if f.get("drug_names"):
        drug_q = Q()
        for drug in f["drug_names"]:
            drug_q |= Q(drugexposure__description__icontains=drug)
        qs = qs.filter(drug_q).distinct()
    if f.get("note_types"):
        qs = qs.filter(note__note_type__in=f["note_types"]).distinct()
    return qs


def _apply_search_boolean_flags(qs: QuerySet, f: dict) -> QuerySet:
    if f.get("has_notes") is True:
        qs = qs.filter(note__isnull=False).distinct()
    for flag, file_type in _FLAG_TO_FILE_TYPE.items():
        if f.get(flag) is True:
            qs = qs.filter(observation__file_type=file_type).distinct()
    return qs
