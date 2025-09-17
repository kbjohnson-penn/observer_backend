"""
Tests for Observation API endpoints.
Basic CRUD operations with authentication and authorization.
"""
from rest_framework import status
from .test_base import BaseResearchAPITestCase
from research.models import Observation, VisitOccurrence
from datetime import date


class ObservationAPITest(BaseResearchAPITestCase):
    """Test cases for Observation API endpoints."""

    def setUp(self):
        super().setUp()  # Sets up authenticated user, profile, tier, person, and provider
        self.visit = VisitOccurrence.objects.using('research').create(
            tier_id=self.tier.id,
            person=self.person,
            provider=self.provider,
            visit_source_id=1
        )
        self.observation = Observation.objects.using('research').create(
            visit_occurrence_id=self.visit.id,
            file_type="patient_view",
            file_path="/data/patient_view_123.mp4",
            observation_date=date.today().isoformat()
        )

    def test_get_observations_authenticated(self):
        """Test retrieving observations for authenticated user."""
        self.authenticate_user()
        
        response = self.client.get('/api/v1/private/observations/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_get_observation_detail_authenticated(self):
        """Test retrieving observation detail for authenticated user."""
        self.authenticate_user()
        
        response = self.client.get(f'/api/v1/private/observations/{self.observation.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.observation.id)

    def test_get_observations_unauthorized(self):
        """Test that unauthenticated requests return 401."""
        response = self.client.get('/api/v1/private/observations/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_observation_detail_unauthorized(self):
        """Test that unauthenticated detail requests return 401."""
        response = self.client.get(f'/api/v1/private/observations/{self.observation.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_observation_detail_not_found(self):
        """Test 404 for non-existent observation ID."""
        self.authenticate_user()
        response = self.client.get('/api/v1/private/observations/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)