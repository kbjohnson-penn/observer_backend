"""
Tests for ProcedureOccurrence API endpoints.
Basic CRUD operations with authentication and authorization.
"""

from rest_framework import status

from research.models import ProcedureOccurrence, VisitOccurrence

from .test_base import BaseResearchAPITestCase


class ProcedureOccurrenceAPITest(BaseResearchAPITestCase):
    """Test cases for ProcedureOccurrence API endpoints."""

    def setUp(self):
        super().setUp()  # Sets up authenticated user, profile, tier, person, and provider
        self.visit = VisitOccurrence.objects.using("research").create(
            tier_level=self.tier.level,
            person=self.person,
            provider=self.provider,
            visit_source_id=1,
        )
        self.procedure_occurrence = ProcedureOccurrence.objects.using("research").create(
            visit_occurrence=self.visit,
            procedure_ordering_date="2025-09-16",
            name="Appendectomy",
            description="Surgical removal of the appendix",
            future_or_stand="STANDARD",
        )

    def test_get_procedures_authenticated(self):
        """Test retrieving procedure occurrences for authenticated user."""
        self.authenticate_user()

        response = self.client.get("/api/v1/research/private/procedure-occurrences/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_get_procedure_detail_authenticated(self):
        """Test retrieving procedure detail for authenticated user."""
        self.authenticate_user()

        response = self.client.get(
            f"/api/v1/research/private/procedure-occurrences/{self.procedure_occurrence.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.procedure_occurrence.id)

    def test_get_procedures_unauthorized(self):
        """Test that unauthenticated requests return 401."""
        response = self.client.get("/api/v1/research/private/procedure-occurrences/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_procedure_detail_unauthorized(self):
        """Test that unauthenticated detail requests return 401."""
        response = self.client.get(
            f"/api/v1/research/private/procedure-occurrences/{self.procedure_occurrence.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_procedure_detail_not_found(self):
        """Test 404 for non-existent procedure occurrence ID."""
        self.authenticate_user()
        response = self.client.get("/api/v1/research/private/procedure-occurrences/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
