"""
Visit search viewset with JSON body-based filtering.
Handles complex filtering across visit, demographic, and clinical data.
"""

from django.db.models import Count, Q

from rest_framework import status as http_status
from rest_framework.response import Response

from research.api.pagination import ResearchPagination
from research.api.serializers import VisitSearchResultSerializer
from research.api.serializers.filter_serializer import FilterSerializer
from research.models import VisitOccurrence
from shared.api.permissions import BaseAuthenticatedViewSet, filter_queryset_by_user_tier


class VisitSearchViewSet(BaseAuthenticatedViewSet):
    """
    ViewSet for complex visit searching with JSON body filters.
    Inherits authentication and permissions from BaseAuthenticatedViewSet.
    Returns comprehensive visit data including patient demographics.
    Only supports POST/create method for searching.
    """

    serializer_class = VisitSearchResultSerializer
    pagination_class = ResearchPagination

    def create(self, request):
        """
        POST endpoint for complex visit filtering with JSON body.
        Accepts nested filter structure and returns paginated results.

        Example request body:
        {
            "filters": {
                "visit": {"tier_id": [1, 2], "date_from": "2020-01-01"},
                "demographics": {"gender": ["Male"], "year_of_birth_from": 1950},
                "clinical": {"labs": {"result_flags": ["abnormal"]}}
            },
            "sort": {"field": "visit_start_date", "direction": "desc"}
        }
        """
        # Validate input
        validator = FilterSerializer(data=request.data)
        if not validator.is_valid():
            return Response(
                {"detail": "Invalid filter parameters", "errors": validator.errors},
                status=http_status.HTTP_400_BAD_REQUEST,
            )

        # Extract validated request data
        filters = request.data.get("filters", {})
        sort_params = request.data.get("sort", {})

        # Start with base queryset filtered by user tier
        queryset = self._get_base_queryset(request.user)
        total_count = queryset.count()

        # Count active filters
        active_filter_count = self._count_active_filters(filters)

        # Apply filters
        queryset = self._apply_visit_filters(queryset, filters.get("visit", {}))
        queryset = self._apply_person_demographic_filters(
            queryset, filters.get("person_demographics", {})
        )
        queryset = self._apply_provider_demographic_filters(
            queryset, filters.get("provider_demographics", {})
        )
        queryset = self._apply_clinical_filters(queryset, filters.get("clinical", {}))

        # Apply sorting
        queryset = self._apply_sorting(queryset, sort_params)

        # Annotate with counts (DISABLED - extremely slow with multiple JOINs and GROUP BY)
        # queryset = self._annotate_counts(queryset)

        # Paginate
        paginator = self.pagination_class()
        paginator.set_metadata(total_count, active_filter_count)

        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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

    def _count_active_filters(self, filters):
        """
        Count the number of active filters in the request.
        """
        count = 0

        # Visit filters
        visit_filters = filters.get("visit", {})
        for key, value in visit_filters.items():
            if value and value != [] and value != "":
                count += 1

        # Person demographics filters
        person_demo_filters = filters.get("person_demographics", {})
        for key, value in person_demo_filters.items():
            if value and value != [] and value != "":
                count += 1

        # Provider demographics filters
        provider_demo_filters = filters.get("provider_demographics", {})
        for key, value in provider_demo_filters.items():
            if value and value != [] and value != "":
                count += 1

        # Clinical filters
        clinical_filters = filters.get("clinical", {})
        for category, category_filters in clinical_filters.items():
            if isinstance(category_filters, dict):
                for key, value in category_filters.items():
                    if value and value != [] and value != "":
                        count += 1

        return count

    def _apply_visit_filters(self, queryset, visit_filters):
        """
        Apply visit-related filters.
        """
        if not visit_filters:
            return queryset

        # Tier filter (multi-select)
        if visit_filters.get("tier_id"):
            queryset = queryset.filter(tier_id__in=visit_filters["tier_id"])

        # Person ID filter
        if visit_filters.get("person_id"):
            queryset = queryset.filter(person_id=visit_filters["person_id"])

        # Provider ID filter
        if visit_filters.get("provider_id"):
            queryset = queryset.filter(provider_id=visit_filters["provider_id"])

        # Visit source filter (multi-select with exact match)
        if visit_filters.get("visit_source_value"):
            visit_source_values = visit_filters["visit_source_value"]
            # Support both array format (preferred) and comma-separated string (legacy)
            if isinstance(visit_source_values, str):
                visit_source_values = [
                    v.strip() for v in visit_source_values.split(",") if v.strip()
                ]
            if visit_source_values:
                queryset = queryset.filter(visit_source_value__in=visit_source_values)

        # Visit source ID filter
        if visit_filters.get("visit_source_id"):
            queryset = queryset.filter(visit_source_id=visit_filters["visit_source_id"])

        # Date range filters
        if visit_filters.get("date_from"):
            queryset = queryset.filter(visit_start_date__gte=visit_filters["date_from"])

        if visit_filters.get("date_to"):
            queryset = queryset.filter(visit_start_date__lte=visit_filters["date_to"])

        return queryset

    def _apply_person_demographic_filters(self, queryset, demo_filters):
        """
        Apply demographic filters (via Person table join).
        """
        if not demo_filters:
            return queryset

        # Gender filter (multi-select)
        if demo_filters.get("gender"):
            queryset = queryset.filter(person__gender_source_value__in=demo_filters["gender"])

        # Race filter (multi-select)
        if demo_filters.get("race"):
            queryset = queryset.filter(person__race_source_value__in=demo_filters["race"])

        # Ethnicity filter (multi-select)
        if demo_filters.get("ethnicity"):
            queryset = queryset.filter(person__ethnicity_source_value__in=demo_filters["ethnicity"])

        # Year of birth range
        if demo_filters.get("year_of_birth_from"):
            queryset = queryset.filter(
                person__year_of_birth__gte=demo_filters["year_of_birth_from"]
            )

        if demo_filters.get("year_of_birth_to"):
            queryset = queryset.filter(person__year_of_birth__lte=demo_filters["year_of_birth_to"])

        return queryset

    def _apply_provider_demographic_filters(self, queryset, provider_demo_filters):
        """
        Apply provider demographic filters (via Provider table join).
        """
        if not provider_demo_filters:
            return queryset

        # Provider gender filter (multi-select)
        if provider_demo_filters.get("gender"):
            queryset = queryset.filter(
                provider__gender_source_value__in=provider_demo_filters["gender"]
            )

        # Provider race filter (multi-select)
        if provider_demo_filters.get("race"):
            queryset = queryset.filter(
                provider__race_source_value__in=provider_demo_filters["race"]
            )

        # Provider ethnicity filter (multi-select)
        if provider_demo_filters.get("ethnicity"):
            queryset = queryset.filter(
                provider__ethnicity_source_value__in=provider_demo_filters["ethnicity"]
            )

        # Provider year of birth range
        if provider_demo_filters.get("year_of_birth_from"):
            queryset = queryset.filter(
                provider__year_of_birth__gte=provider_demo_filters["year_of_birth_from"]
            )

        if provider_demo_filters.get("year_of_birth_to"):
            queryset = queryset.filter(
                provider__year_of_birth__lte=provider_demo_filters["year_of_birth_to"]
            )

        return queryset

    def _apply_clinical_filters(self, queryset, clinical_filters):
        """
        Apply clinical data filters (via related tables).
        IMPORTANT: Labs are linked through person__labs__ because Labs FK is to Person, not VisitOccurrence.
        """
        if not clinical_filters:
            return queryset

        # Conditions filters
        conditions = clinical_filters.get("conditions", {})
        if conditions:
            if conditions.get("condition_codes"):
                queryset = queryset.filter(
                    conditionoccurrence__concept_code__in=conditions["condition_codes"]
                )

            if conditions.get("condition_source_values"):
                # Apply OR condition for each search term
                condition_query = Q()
                for term in conditions["condition_source_values"]:
                    condition_query |= Q(
                        conditionoccurrence__condition_source_value__icontains=term
                    )
                queryset = queryset.filter(condition_query)

            if conditions.get("is_primary_dx") is not None:
                queryset = queryset.filter(
                    conditionoccurrence__is_primary_dx=conditions["is_primary_dx"]
                )

        # Labs filters (Labs is linked to Person, not Visit, so we filter through person)
        labs = clinical_filters.get("labs", {})
        if labs:
            if labs.get("procedure_names"):
                queryset = queryset.filter(person__labs__procedure_name__in=labs["procedure_names"])

            if labs.get("result_flags"):
                queryset = queryset.filter(person__labs__result_flag__in=labs["result_flags"])

            if labs.get("order_statuses"):
                queryset = queryset.filter(person__labs__order_status__in=labs["order_statuses"])

        # Drugs filters
        drugs = clinical_filters.get("drugs", {})
        if drugs and drugs.get("descriptions"):
            drug_query = Q()
            for term in drugs["descriptions"]:
                drug_query |= Q(drugexposure__description__icontains=term)
            queryset = queryset.filter(drug_query)

        # Procedures filters
        procedures = clinical_filters.get("procedures", {})
        if procedures:
            if procedures.get("names"):
                queryset = queryset.filter(procedureoccurrence__name__in=procedures["names"])

            if procedures.get("future_or_stand"):
                queryset = queryset.filter(
                    procedureoccurrence__future_or_stand=procedures["future_or_stand"]
                )

        # Notes filters
        notes = clinical_filters.get("notes", {})
        if notes:
            if notes.get("note_types"):
                queryset = queryset.filter(note__note_type__in=notes["note_types"])

            if notes.get("note_statuses"):
                queryset = queryset.filter(note__note_status__in=notes["note_statuses"])

        # Observations filters
        observations = clinical_filters.get("observations", {})
        if observations and observations.get("file_types"):
            queryset = queryset.filter(observation__file_type__in=observations["file_types"])

        # Measurements filters
        measurements = clinical_filters.get("measurements", {})
        if measurements:
            if measurements.get("bp_systolic_min"):
                queryset = queryset.filter(
                    measurement__bp_systolic__gte=measurements["bp_systolic_min"]
                )

            if measurements.get("bp_systolic_max"):
                queryset = queryset.filter(
                    measurement__bp_systolic__lte=measurements["bp_systolic_max"]
                )

            if measurements.get("weight_lb_min"):
                queryset = queryset.filter(
                    measurement__weight_lb__gte=measurements["weight_lb_min"]
                )

            if measurements.get("weight_lb_max"):
                queryset = queryset.filter(
                    measurement__weight_lb__lte=measurements["weight_lb_max"]
                )

        # DISTINCT can be slow with many joins - only use when filtering by clinical data
        if clinical_filters:
            return queryset.distinct()
        return queryset

    def _apply_sorting(self, queryset, sort_params):
        """
        Apply sorting to the queryset.
        """
        if not sort_params:
            return queryset.order_by("-visit_start_date", "-visit_start_time")

        field = sort_params.get("field", "visit_start_date")
        direction = sort_params.get("direction", "desc")

        # Map frontend field names to model field names
        field_mapping = {
            "id": "id",
            "visit_start_date": "visit_start_date",
            "visit_source_value": "visit_source_value",
            "tier_id": "tier_id",
            "person_id": "person_id",
            "provider_id": "provider_id",
        }

        order_field = field_mapping.get(field, "visit_start_date")

        if direction == "desc":
            order_field = f"-{order_field}"

        return queryset.order_by(order_field)

    def _annotate_counts(self, queryset):
        """
        Annotate queryset with counts of related clinical data.
        This is optional but useful for frontend display.
        DISABLED due to performance - re-enable if needed.
        """
        return queryset.annotate(
            condition_count=Count("conditionoccurrence", distinct=True),
            drug_count=Count("drugexposure", distinct=True),
            procedure_count=Count("procedureoccurrence", distinct=True),
            lab_count=Count("person__labs", distinct=True),  # Labs linked through person
            note_count=Count("note", distinct=True),
            observation_count=Count("observation", distinct=True),
            measurement_count=Count("measurement", distinct=True),
        )
