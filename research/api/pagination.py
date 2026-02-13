"""
Custom pagination class for research API endpoints.
Extends DRF's PageNumberPagination to add filter summary metadata.
Base pagination settings (page_size) are inherited from settings.py.
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ResearchPagination(PageNumberPagination):
    """
    Custom pagination class that includes filter summary metadata.
    Inherits page_size from REST_FRAMEWORK['PAGE_SIZE'] in settings.py (20).
    Allows users to override page size via query param up to max_page_size.
    """

    page_size_query_param = "page_size"  # Allows ?page_size=50
    max_page_size = 100  # Maximum allowed override

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_count = None
        self.active_filter_count = 0

    def set_metadata(self, total_count, active_filter_count):
        """
        Set additional metadata for the pagination response.

        Args:
            total_count: Total number of items without filters
            active_filter_count: Number of active filters applied
        """
        self.total_count = total_count
        self.active_filter_count = active_filter_count

    def get_paginated_response(self, data):
        """
        Return paginated response with additional filter metadata.
        """
        response_data = {
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,
        }

        # Add filter summary if metadata was set
        if self.total_count is not None:
            response_data["filter_summary"] = {
                "total_visits": self.total_count,
                "filtered_visits": self.page.paginator.count,
                "active_filters": self.active_filter_count,
            }

        return Response(response_data)
