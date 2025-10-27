"""
Cohort ViewSet for accounts API.
Provides CRUD operations for user cohorts.
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.api.serializers import (
    CohortCreateSerializer,
    CohortListSerializer,
    CohortSerializer,
    CohortUpdateSerializer,
)
from accounts.models import Cohort
from shared.api.permissions import BaseAuthenticatedViewSet


class CohortViewSet(BaseAuthenticatedViewSet):
    """
    ViewSet for cohort management.

    Endpoints:
        GET    /api/v1/accounts/cohorts/          - List user's cohorts
        POST   /api/v1/accounts/cohorts/          - Create new cohort
        GET    /api/v1/accounts/cohorts/{id}/     - Get cohort detail
        PUT    /api/v1/accounts/cohorts/{id}/     - Update cohort
        PATCH  /api/v1/accounts/cohorts/{id}/     - Partial update
        DELETE /api/v1/accounts/cohorts/{id}/     - Delete cohort
        POST   /api/v1/accounts/cohorts/{id}/duplicate/ - Duplicate cohort

    Permissions:
        - User must be authenticated
        - Users can only access their own cohorts
    """

    def get_queryset(self):
        """
        Return cohorts owned by the current user only.
        Orders by creation date (newest first).
        """
        return (
            Cohort.objects.using("accounts").filter(user=self.request.user).order_by("-created_at")
        )

    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        """
        if self.action == "list":
            return CohortListSerializer
        elif self.action == "create":
            return CohortCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return CohortUpdateSerializer
        return CohortSerializer

    def list(self, request):
        """
        GET /api/v1/accounts/cohorts/

        Returns list of user's cohorts with filter summaries.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(
            {
                "cohorts": serializer.data,
                "count": queryset.count(),
            }
        )

    def create(self, request):
        """
        POST /api/v1/accounts/cohorts/

        Create a new cohort for the current user.

        Request Body:
        {
            "name": "High Blood Pressure Patients",
            "description": "Patients with systolic BP > 140",
            "filters": {
                "visit": {...},
                "person_demographics": {...},
                "provider_demographics": {...},
                "clinical": {...}
            },
            "visit_count": 234
        }
        """
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # Save with current user
        cohort = serializer.save(user=request.user)

        # Return full cohort data
        return_serializer = CohortSerializer(cohort)
        return Response(return_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """
        GET /api/v1/accounts/cohorts/{id}/

        Get detailed information about a specific cohort.
        """
        try:
            cohort = self.get_queryset().get(pk=pk)
        except Cohort.DoesNotExist:
            return Response(
                {"detail": f"Cohort with ID {pk} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(cohort)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """
        PUT /api/v1/accounts/cohorts/{id}/

        Update cohort (full update).
        """
        try:
            cohort = self.get_queryset().get(pk=pk)
        except Cohort.DoesNotExist:
            return Response(
                {"detail": f"Cohort with ID {pk} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(cohort, data=request.data)

        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        # Return full cohort data
        return_serializer = CohortSerializer(cohort)
        return Response(return_serializer.data)

    def partial_update(self, request, pk=None):
        """
        PATCH /api/v1/accounts/cohorts/{id}/

        Partial update of cohort (only provided fields updated).
        """
        try:
            cohort = self.get_queryset().get(pk=pk)
        except Cohort.DoesNotExist:
            return Response(
                {"detail": f"Cohort with ID {pk} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(cohort, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        # Return full cohort data
        return_serializer = CohortSerializer(cohort)
        return Response(return_serializer.data)

    def destroy(self, request, pk=None):
        """
        DELETE /api/v1/accounts/cohorts/{id}/

        Delete a cohort.
        """
        try:
            cohort = self.get_queryset().get(pk=pk)
        except Cohort.DoesNotExist:
            return Response(
                {"detail": f"Cohort with ID {pk} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        cohort.delete()

        return Response(
            {"detail": "Cohort deleted successfully."}, status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        """
        POST /api/v1/accounts/cohorts/{id}/duplicate/

        Create a duplicate of an existing cohort with a new name.

        Request Body:
        {
            "name": "Copy of Original Cohort"
        }
        """
        try:
            original_cohort = self.get_queryset().get(pk=pk)
        except Cohort.DoesNotExist:
            return Response(
                {"detail": f"Cohort with ID {pk} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get new name from request
        new_name = request.data.get("name")
        if not new_name:
            new_name = f"Copy of {original_cohort.name}"

        # Create duplicate
        duplicate = Cohort.objects.using("accounts").create(
            user=request.user,
            name=new_name,
            description=original_cohort.description,
            filters=original_cohort.filters,
            visit_count=original_cohort.visit_count,
        )

        serializer = CohortSerializer(duplicate)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
