"""
Cohort Data ViewSet for fetching all OMOP table data filtered by cohort criteria.
Returns data in SampleDataAPIResponse format for HealthcareDataBrowser component.
"""

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

            # 3. Get filtered visits using cohort's saved filters
            queryset = self._get_base_queryset(request.user)
            queryset = self._apply_filters(queryset, cohort.filters or {})

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
            related_field="tier_id",
        )

    def _apply_filters(self, queryset, filters):
        """
        Apply cohort filters to visits queryset.
        Reuses filtering logic from VisitSearchViewSet.

        Args:
            queryset: Base VisitOccurrence queryset
            filters: Cohort filters dict (same structure as visit search filters)

        Returns:
            Filtered queryset
        """
        # Import VisitSearchViewSet to reuse filter methods
        from research.api.viewsets.private.visit_search_viewset import VisitSearchViewSet

        # Create temporary instance to use filter methods
        vs = VisitSearchViewSet()

        # Apply each filter type
        queryset = vs._apply_visit_filters(queryset, filters.get("visit", {}))
        queryset = vs._apply_person_demographic_filters(
            queryset, filters.get("person_demographics", {})
        )
        queryset = vs._apply_provider_demographic_filters(
            queryset, filters.get("provider_demographics", {})
        )
        queryset = vs._apply_clinical_filters(queryset, filters.get("clinical", {}))

        return queryset
