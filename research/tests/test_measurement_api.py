"""
Tests for Measurement API endpoints.
Basic CRUD operations with authentication and authorization.
"""

from rest_framework import status

from research.models import Measurement, VisitOccurrence

from .test_base import BaseResearchAPITestCase


class MeasurementAPITest(BaseResearchAPITestCase):
    """Test cases for Measurement API endpoints."""

    def setUp(self):
        super().setUp()  # Sets up authenticated user, profile, tier, person, and provider
        self.visit = VisitOccurrence.objects.using("research").create(
            tier_id=self.tier.id, person=self.person, provider=self.provider, visit_source_id=1
        )
        self.measurement = Measurement.objects.using("research").create(
            visit_occurrence=self.visit,
            bp_systolic=120,
            bp_diastolic=80,
            phys_bp="120/80",
            weight_lb=150.5,
            height="5'10\"",
            pulse=72,
            phys_spo2=98,
        )

    def test_get_measurements_authenticated(self):
        """Test retrieving measurement records for authenticated user."""
        self.authenticate_user()

        response = self.client.get("/api/v1/research/private/measurements/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_get_measurement_detail_authenticated(self):
        """Test retrieving measurement detail for authenticated user."""
        self.authenticate_user()

        response = self.client.get(f"/api/v1/research/private/measurements/{self.measurement.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.measurement.id)

    def test_get_measurements_unauthorized(self):
        """Test that unauthenticated requests return 401."""
        response = self.client.get("/api/v1/research/private/measurements/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_measurement_detail_unauthorized(self):
        """Test that unauthenticated detail requests return 401."""
        response = self.client.get(f"/api/v1/research/private/measurements/{self.measurement.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_measurement_detail_not_found(self):
        """Test 404 for non-existent measurement ID."""
        self.authenticate_user()
        response = self.client.get("/api/v1/research/private/measurements/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
