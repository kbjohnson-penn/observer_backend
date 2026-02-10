"""
Tests for ConditionOccurrence API endpoints.
Basic CRUD operations with authentication and authorization.
"""

from rest_framework import status

from research.models import ConditionOccurrence, VisitOccurrence

from .test_base import BaseResearchAPITestCase


class ConditionOccurrenceAPITest(BaseResearchAPITestCase):
    """Test cases for ConditionOccurrence API endpoints."""

    def setUp(self):
        super().setUp()  # Sets up authenticated user, profile, tier, person, and provider
        self.visit = VisitOccurrence.objects.using("research").create(
            tier_level=self.tier.level,
            person=self.person,
            provider=self.provider,
            visit_source_id=1,
        )
        self.condition_occurrence = ConditionOccurrence.objects.using("research").create(
            visit_occurrence=self.visit,
            is_primary_dx="Y",
            condition_source_value="Hypertension",
            condition_concept_id=320128,
            concept_code="I10",
        )

    def test_get_conditions_authenticated(self):
        """Test retrieving condition occurrences for authenticated user."""
        self.authenticate_user()

        response = self.client.get("/api/v1/research/private/condition-occurrences/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_get_condition_detail_authenticated(self):
        """Test retrieving condition detail for authenticated user."""
        self.authenticate_user()

        response = self.client.get(
            f"/api/v1/research/private/condition-occurrences/{self.condition_occurrence.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.condition_occurrence.id)

    def test_get_conditions_unauthorized(self):
        """Test that unauthenticated requests return 401."""
        response = self.client.get("/api/v1/research/private/condition-occurrences/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_condition_detail_unauthorized(self):
        """Test that unauthenticated detail requests return 401."""
        response = self.client.get(
            f"/api/v1/research/private/condition-occurrences/{self.condition_occurrence.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_condition_detail_not_found(self):
        """Test 404 for non-existent condition occurrence ID."""
        self.authenticate_user()
        response = self.client.get("/api/v1/research/private/condition-occurrences/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
