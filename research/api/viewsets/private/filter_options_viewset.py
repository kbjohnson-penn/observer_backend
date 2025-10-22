"""
Filter options viewset to provide dynamic filter values to frontend.
Returns all available values for dropdown filters based on user's tier access.
Uses hybrid approach: static values for common data, cached queries for visit metadata.
"""

from django.db.models import Max, Min
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.response import Response

from research.models import Person, Provider, VisitOccurrence
from shared.api.permissions import BaseAuthenticatedViewSet, filter_queryset_by_user_tier


class FilterOptionsViewSet(BaseAuthenticatedViewSet):
    """
    ViewSet for retrieving filter options.
    Only implements list() method - no CRUD operations.
    Cached for 5 minutes to improve performance.
    """

    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def list(self, request):
        """
        GET endpoint that returns all available filter options based on user's tier access.
        """
        user = request.user

        # Get accessible visits based on user tier
        accessible_visits = filter_queryset_by_user_tier(
            VisitOccurrence.objects.using("research"), user, related_field="tier_id"
        )

        # Demographics options - query actual values from both Person and Provider tables
        # Get unique person and provider IDs from accessible visits
        accessible_person_ids = accessible_visits.values_list("person_id", flat=True).distinct()
        accessible_provider_ids = accessible_visits.values_list("provider_id", flat=True).distinct()

        # Query Person and Provider tables for actual demographic values
        accessible_persons = Person.objects.using("research").filter(id__in=accessible_person_ids)
        accessible_providers = Provider.objects.using("research").filter(
            id__in=accessible_provider_ids
        )

        # Combine unique values from both patients and providers
        patient_genders = set(
            accessible_persons.values_list("gender_source_value", flat=True)
            .exclude(gender_source_value__isnull=True)
            .exclude(gender_source_value="")
        )
        provider_genders = set(
            accessible_providers.values_list("gender_source_value", flat=True)
            .exclude(gender_source_value__isnull=True)
            .exclude(gender_source_value="")
        )
        all_genders = sorted(patient_genders | provider_genders)

        patient_races = set(
            accessible_persons.values_list("race_source_value", flat=True)
            .exclude(race_source_value__isnull=True)
            .exclude(race_source_value="")
        )
        provider_races = set(
            accessible_providers.values_list("race_source_value", flat=True)
            .exclude(race_source_value__isnull=True)
            .exclude(race_source_value="")
        )
        all_races = sorted(patient_races | provider_races)

        patient_ethnicities = set(
            accessible_persons.values_list("ethnicity_source_value", flat=True)
            .exclude(ethnicity_source_value__isnull=True)
            .exclude(ethnicity_source_value="")
        )
        provider_ethnicities = set(
            accessible_providers.values_list("ethnicity_source_value", flat=True)
            .exclude(ethnicity_source_value__isnull=True)
            .exclude(ethnicity_source_value="")
        )
        all_ethnicities = sorted(patient_ethnicities | provider_ethnicities)

        # Get year of birth ranges for both
        person_yob = accessible_persons.aggregate(
            min=Min("year_of_birth"), max=Max("year_of_birth")
        )
        provider_yob = accessible_providers.aggregate(
            min=Min("year_of_birth"), max=Max("year_of_birth")
        )

        yob_min = (
            min(person_yob["min"] or 9999, provider_yob["min"] or 9999)
            if (person_yob["min"] or provider_yob["min"])
            else None
        )

        yob_max = (
            max(person_yob["max"] or 0, provider_yob["max"] or 0)
            if (person_yob["max"] or provider_yob["max"])
            else None
        )

        demographics = {
            "genders": all_genders,
            "races": all_races,
            "ethnicities": all_ethnicities,
            "year_of_birth_range": {"min": yob_min, "max": yob_max},
        }

        # Visit options - cached real-time queries
        visit_date_range = accessible_visits.aggregate(
            earliest=Min("visit_start_date"), latest=Max("visit_start_date")
        )

        visit_options = {
            "tiers": list(
                accessible_visits.values_list("tier_id", flat=True).distinct().order_by("tier_id")
            ),
            "visit_sources": list(
                accessible_visits.values_list("visit_source_value", flat=True)
                .distinct()
                .exclude(visit_source_value__isnull=True)
                .exclude(visit_source_value="")
                .order_by("visit_source_value")
            ),
            "date_range": {
                "earliest": (
                    visit_date_range["earliest"].isoformat()
                    if visit_date_range["earliest"]
                    else None
                ),
                "latest": (
                    visit_date_range["latest"].isoformat() if visit_date_range["latest"] else None
                ),
            },
        }

        # Clinical options - using static/common values for performance
        # Empty arrays for autocomplete-based filters (labs, conditions, drugs, procedures)
        # Static arrays for known/standard values (result flags, statuses, types)
        clinical_options = {
            "conditions": {
                "available_codes": [],  # Empty - populate via autocomplete endpoint
                "available_values": [],
                "total_visits": 0,
            },
            "labs": {
                "procedure_names": [],  # Empty - populate via autocomplete endpoint
                "result_flags": ["normal", "abnormal", "critical", "low", "high"],
                "order_statuses": ["Complete", "Final", "Pending", "In Progress"],
                "total_visits": 0,
            },
            "drugs": {"common_drugs": [], "total_visits": 0},
            "procedures": {
                "common_names": [],
                "future_or_stand_options": ["Future", "Standing", "Normal"],
                "total_visits": 0,
            },
            "notes": {
                "note_types": [
                    "Progress Note",
                    "Discharge Summary",
                    "Consultation",
                    "History and Physical",
                ],
                "note_statuses": ["Final", "Amended", "Preliminary", "In Progress"],
                "total_visits": 0,
            },
            "observations": {
                "file_types": ["image", "video", "audio", "document"],
                "total_visits": 0,
            },
            "measurements": {
                "total_visits": 0,
                "bp_systolic_range": {"min": 80, "max": 200},
                "weight_range": {"min": 50, "max": 400},
            },
        }

        return Response(
            {
                "demographics": demographics,
                "visit_options": visit_options,
                "clinical_options": clinical_options,
                "total_accessible_visits": accessible_visits.count(),
            }
        )
