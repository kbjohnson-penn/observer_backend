"""
Tests for DrugExposure API endpoints.
Basic CRUD operations with authentication and authorization.
"""
from rest_framework import status
from django.utils import timezone
import pytz
from .test_base import BaseResearchAPITestCase
from research.models import DrugExposure, VisitOccurrence


class DrugExposureAPITest(BaseResearchAPITestCase):
    """Test cases for DrugExposure API endpoints."""

    def setUp(self):
        super().setUp()  # Sets up authenticated user, profile, tier, person, and provider
        self.visit = VisitOccurrence.objects.using('research').create(
            tier_id=self.tier.id,
            person=self.person,
            provider=self.provider,
            visit_source_id=1
        )
        self.drug_exposure = DrugExposure.objects.using('research').create(
            visit_occurrence_id=self.visit.id,
            drug_ordering_date="2023-01-01",
            drug_exposure_start_datetime=timezone.datetime(2023, 1, 1, 9, 0, tzinfo=pytz.UTC),
            drug_exposure_end_datetime=timezone.datetime(2023, 1, 2, 9, 0, tzinfo=pytz.UTC),
            description="Ibuprofen 200mg",
            quantity="30 tablets"
        )

    def test_get_drug_exposures_authenticated(self):
        """Test retrieving drug exposures for authenticated user."""
        self.authenticate_user()
        
        response = self.client.get('/api/v1/research/private/drug-exposures/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_get_drug_exposure_detail_authenticated(self):
        """Test retrieving drug exposure detail for authenticated user."""
        self.authenticate_user()
        
        response = self.client.get(f'/api/v1/research/private/drug-exposures/{self.drug_exposure.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.drug_exposure.id)

    def test_get_drug_exposures_unauthorized(self):
        """Test that unauthenticated requests return 401."""
        response = self.client.get('/api/v1/research/private/drug-exposures/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_drug_exposure_detail_unauthorized(self):
        """Test that unauthenticated detail requests return 401."""
        response = self.client.get(f'/api/v1/research/private/drug-exposures/{self.drug_exposure.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_drug_exposure_detail_not_found(self):
        """Test 404 for non-existent drug exposure ID."""
        self.authenticate_user()
        response = self.client.get('/api/v1/research/private/drug-exposures/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)