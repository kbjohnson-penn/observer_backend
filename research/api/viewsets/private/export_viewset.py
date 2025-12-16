"""
Export ViewSet for server-side data exports with automatic audit logging.

This viewset handles all export operations, fetching data server-side
with tier-based access control, generating CSV/ZIP files, and logging
each export for HIPAA compliance.
"""

import re
from typing import Optional

from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator

from django_ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from accounts.models import AuditTrail, Cohort
from accounts.services import AuditService
from research.models import (
    AuditLogs,
    ConditionOccurrence,
    DrugExposure,
    Labs,
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
from research.services.export_service import ExportService
from shared.api.permissions import filter_queryset_by_user_tier

# Maximum number of records allowed per export to prevent memory exhaustion
MAX_EXPORT_RECORDS = 100000


class ExportLimitExceededError(Exception):
    """Raised when export exceeds maximum allowed records."""

    pass


# Mapping from frontend table IDs to model info
TABLE_REGISTRY = {
    "persons": {"model": Person, "filter_field": "id__in", "id_source": "person_ids"},
    "providers": {"model": Provider, "filter_field": "id__in", "id_source": "provider_ids"},
    "visits": {"model": VisitOccurrence, "filter_field": None, "id_source": None},  # Base table
    "notes": {"model": Note, "filter_field": "visit_occurrence_id__in", "id_source": "visit_ids"},
    "conditions": {
        "model": ConditionOccurrence,
        "filter_field": "visit_occurrence_id__in",
        "id_source": "visit_ids",
    },
    "drugs": {
        "model": DrugExposure,
        "filter_field": "visit_occurrence_id__in",
        "id_source": "visit_ids",
    },
    "procedures": {
        "model": ProcedureOccurrence,
        "filter_field": "visit_occurrence_id__in",
        "id_source": "visit_ids",
    },
    "measurements": {
        "model": Measurement,
        "filter_field": "visit_occurrence_id__in",
        "id_source": "visit_ids",
    },
    "observations": {
        "model": Observation,
        "filter_field": "visit_occurrence_id__in",
        "id_source": "visit_ids",
    },
    "patient_surveys": {
        "model": PatientSurvey,
        "filter_field": "visit_occurrence_id__in",
        "id_source": "visit_ids",
    },
    "provider_surveys": {
        "model": ProviderSurvey,
        "filter_field": "visit_occurrence_id__in",
        "id_source": "visit_ids",
    },
    "audit_logs": {
        "model": AuditLogs,
        "filter_field": "visit_occurrence_id__in",
        "id_source": "visit_ids",
    },
    "labs": {"model": Labs, "filter_field": "person_id__in", "id_source": "person_ids"},
}


@method_decorator(
    ratelimit(key="user", rate=settings.RATE_LIMITS["DATA_EXPORT"], method="POST", block=True),
    name="single_table",
)
@method_decorator(
    ratelimit(key="user", rate=settings.RATE_LIMITS["DATA_EXPORT"], method="POST", block=True),
    name="all_tables",
)
class ExportViewSet(ViewSet):
    """
    ViewSet for exporting research data with automatic audit logging.

    Data is fetched server-side with tier-based access control, ensuring
    users can only export data they have permission to access.

    All exports are logged to the AuditTrail for HIPAA compliance.
    Audit logging happens in the same request as export generation,
    ensuring bulletproof compliance tracking.

    Rate limited to prevent abuse (configured via RATE_LIMIT_DATA_EXPORT).
    """

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.export_service = ExportService()

    def _validate_cohort_id(self, cohort_id) -> tuple[Optional[int], Optional[Response]]:
        """Validate cohort_id parameter. Returns (validated_id, error_response)."""
        if not cohort_id:
            return None, Response(
                {"error": "cohort_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            return int(cohort_id), None
        except (TypeError, ValueError):
            return None, Response(
                {"error": "cohort_id must be an integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def _validate_table_id(self, table_id) -> Optional[Response]:
        """Validate table_id parameter. Returns error response or None if valid."""
        if not table_id:
            return Response(
                {"error": "table_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if table_id not in TABLE_REGISTRY:
            return Response(
                {"error": f"Invalid table_id: {table_id}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return None

    def _get_cohort_for_user(
        self, cohort_id: int, user
    ) -> tuple[Optional[Cohort], Optional[Response]]:
        """Fetch cohort and verify ownership. Returns (cohort, error_response)."""
        try:
            cohort = Cohort.objects.using("accounts").get(pk=cohort_id)
            if cohort.user_id != user.id:
                return None, Response(
                    {"error": "You do not have permission to export this cohort's data"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            return cohort, None
        except Cohort.DoesNotExist:
            return None, Response(
                {"error": f"Cohort with ID {cohort_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["post"])
    def single_table(self, request):
        """
        Export a single table as CSV or ZIP (with docs).

        Data is fetched server-side with tier-based access control.

        Request body:
            - cohort_id: int - ID of the cohort to export data for
            - table_id: string - identifier for the table (e.g., "persons", "visits")
            - include_docs: bool - whether to include documentation (creates ZIP)

        Returns:
            CSV file or ZIP file as attachment
        """
        table_id = request.data.get("table_id")
        include_docs = request.data.get("include_docs", False)

        # Validate inputs
        cohort_id, error = self._validate_cohort_id(request.data.get("cohort_id"))
        if error:
            return error

        error = self._validate_table_id(table_id)
        if error:
            return error

        cohort, error = self._get_cohort_for_user(cohort_id, request.user)
        if error:
            return error

        # Fetch data server-side with tier filtering
        try:
            tables_data = self._fetch_cohort_data(request.user, cohort, [table_id])
        except ExportLimitExceededError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = tables_data.get(table_id, [])

        # Get model field names for headers (used if data is empty)
        table_headers = self._get_table_headers([table_id])
        fieldnames = table_headers.get(table_id)

        # Generate export
        if include_docs:
            content = self.export_service.generate_zip(
                {table_id: data}, include_docs=True, table_headers=table_headers
            )
            content_type = "application/zip"
            filename = f"{table_id}_export.zip"
            event_type = "EXPORT_SINGLE_TABLE_WITH_DOCS"
        else:
            content = self.export_service.generate_csv(table_id, data, fieldnames)
            content_type = "text/csv; charset=utf-8"
            filename = f"{table_id}.csv"
            event_type = "EXPORT_SINGLE_TABLE_CSV"

        # Log audit trail (same request = bulletproof)
        self._log_export(
            request=request,
            event_type=event_type,
            table_id=table_id,
            record_count=len(data),
            include_docs=include_docs,
            cohort_id=cohort_id,
            cohort_name=cohort.name,
        )

        response = HttpResponse(content, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    @action(detail=False, methods=["post"])
    def all_tables(self, request):
        """
        Export all tables as a ZIP file.

        Data is fetched server-side with tier-based access control.

        Request body:
            - cohort_id: int - ID of the cohort to export data for
            - include_docs: bool - whether to include documentation

        Returns:
            ZIP file as attachment
        """
        include_docs = request.data.get("include_docs", False)

        # Validate inputs
        cohort_id, error = self._validate_cohort_id(request.data.get("cohort_id"))
        if error:
            return error

        cohort, error = self._get_cohort_for_user(cohort_id, request.user)
        if error:
            return error

        # Fetch all table data server-side with tier filtering
        all_table_ids = list(TABLE_REGISTRY.keys())
        try:
            tables_data = self._fetch_cohort_data(request.user, cohort, all_table_ids)
        except ExportLimitExceededError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total_records = sum(len(data) for data in tables_data.values())
        table_count = len([t for t in tables_data.values() if t])  # Count non-empty tables

        # Get model field names for empty table headers
        table_headers = self._get_table_headers(all_table_ids)

        # Generate export
        content = self.export_service.generate_zip(tables_data, include_docs, table_headers)

        # Log audit trail
        event_type = "EXPORT_ALL_TABLES_WITH_DOCS" if include_docs else "EXPORT_ALL_TABLES_CSV"
        self._log_export(
            request=request,
            event_type=event_type,
            table_id=None,
            record_count=total_records,
            include_docs=include_docs,
            table_count=table_count,
            cohort_id=cohort_id,
            cohort_name=cohort.name,
        )

        response = HttpResponse(content, content_type="application/zip")
        safe_name = self._sanitize_filename(cohort.name)
        response["Content-Disposition"] = f'attachment; filename="{safe_name}_export.zip"'
        return response

    def _fetch_cohort_data(
        self, user, cohort: Cohort, table_ids: list[str]
    ) -> dict[str, list[dict]]:
        """
        Fetch data for specified tables from a cohort with tier-based filtering.

        This reuses the same filtering logic as CohortDataViewSet to ensure
        consistent tier-based access control.

        Args:
            user: The requesting user
            cohort: The Cohort object
            table_ids: List of table IDs to fetch

        Returns:
            Dict mapping table_id to list of records as dicts
        """
        # Import here to avoid circular imports
        from research.api.viewsets.private.visit_search_viewset import VisitSearchViewSet

        # Get base visits queryset with tier filtering
        base_queryset = filter_queryset_by_user_tier(
            VisitOccurrence.objects.using("research").select_related("person", "provider").all(),
            user,
            related_field="tier_id",
        )

        # Apply cohort filters
        vs = VisitSearchViewSet()
        filters = cohort.filters or {}
        queryset = vs._apply_visit_filters(base_queryset, filters.get("visit", {}))
        queryset = vs._apply_person_demographic_filters(
            queryset, filters.get("person_demographics", {})
        )
        queryset = vs._apply_provider_demographic_filters(
            queryset, filters.get("provider_demographics", {})
        )
        queryset = vs._apply_clinical_filters(queryset, filters.get("clinical", {}))

        # Check record count before loading into memory
        record_count = queryset.count()
        if record_count > MAX_EXPORT_RECORDS:
            raise ExportLimitExceededError(
                f"Export exceeds maximum of {MAX_EXPORT_RECORDS:,} records. "
                f"This cohort contains {record_count:,} visits. Please refine your cohort filters."
            )

        # Get visits and extract IDs
        visits = list(queryset.values())
        visit_ids = [v["id"] for v in visits]
        person_ids = list(set([v["person_id"] for v in visits]))
        provider_ids = list(set([v["provider_id"] for v in visits if v["provider_id"]]))

        # Build ID lookup for filtering
        id_sources = {
            "visit_ids": visit_ids,
            "person_ids": person_ids,
            "provider_ids": provider_ids,
        }

        # Fetch requested tables
        result = {}
        for table_id in table_ids:
            if table_id not in TABLE_REGISTRY:
                continue

            config = TABLE_REGISTRY[table_id]

            if table_id == "visits":
                # Visits are already fetched
                result[table_id] = visits
            else:
                # Fetch from model with appropriate filter
                model = config["model"]
                filter_field = config["filter_field"]
                id_source = config["id_source"]

                if id_source and filter_field:
                    ids = id_sources.get(id_source, [])
                    if ids:
                        result[table_id] = list(
                            model.objects.using("research").filter(**{filter_field: ids}).values()
                        )
                    else:
                        result[table_id] = []
                else:
                    result[table_id] = []

        return result

    def _log_export(
        self,
        request,
        event_type: str,
        table_id: Optional[str],
        record_count: int,
        include_docs: bool,
        table_count: Optional[int] = None,
        cohort_id: Optional[int] = None,
        cohort_name: Optional[str] = None,
    ) -> None:
        """
        Create audit trail entry for export.

        This is called in the same request as export generation,
        ensuring the audit log is always created when an export happens.
        """
        # Sanitize cohort_name to prevent log injection
        safe_cohort_name = AuditService._sanitize_string(cohort_name or "", max_length=100)

        AuditTrail.objects.using("accounts").create(
            user=request.user,
            event_type=event_type,
            category="DATA_EXPORT",
            description=f"Exported {record_count} records from cohort '{safe_cohort_name}'",
            metadata={
                "table_id": table_id,
                "table_count": table_count,
                "record_count": record_count,
                "include_docs": include_docs,
                "cohort_id": cohort_id,
                "cohort_name": safe_cohort_name,
            },
            ip_address=AuditService.get_client_ip(request),
            user_agent=AuditService._sanitize_user_agent(request.META.get("HTTP_USER_AGENT", "")),
        )

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for Content-Disposition header.

        Removes characters that could cause header injection or filesystem issues.
        """
        # Remove/replace dangerous characters (quotes, newlines, path separators, etc.)
        sanitized = re.sub(r'["\n\r\\/:*?<>|]', "_", filename)
        # Limit length to prevent overly long filenames
        return sanitized[:100]

    def _get_table_headers(self, table_ids: list[str]) -> dict[str, list[str]]:
        """
        Get column names for each table from model field definitions.

        Args:
            table_ids: List of table IDs to get headers for

        Returns:
            Dict mapping table_id to list of column names
        """
        headers = {}
        for table_id in table_ids:
            if table_id not in TABLE_REGISTRY:
                continue
            model = TABLE_REGISTRY[table_id]["model"]
            # Get field names from model meta
            field_names = [field.name for field in model._meta.get_fields() if field.concrete]
            headers[table_id] = field_names
        return headers
