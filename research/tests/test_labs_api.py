"""
Tests for Labs API endpoints.
Basic CRUD operations with authentication and authorization.
"""
from rest_framework import status
from django.utils import timezone
import pytz
from .test_base import BaseResearchAPITestCase
from research.models import Labs, Person, VisitOccurrence


class LabsAPITest(BaseResearchAPITestCase):
    """Test cases for Labs API endpoints."""

    def setUp(self):
        super().setUp()  # Sets up authenticated user, profile, tier, person, and provider
        # Create a VisitOccurrence instance with tier_id
        self.visit = VisitOccurrence.objects.using('research').create(
            tier_id=self.tier.id,
            person=self.person,
            provider=self.provider,
            visit_source_id=1
        )
        # Create Labs instance linked to Person
        self.lab = Labs.objects.using('research').create(
            person=self.person,
            ordering_date_shifted=timezone.datetime(2023, 1, 1, 9, 0, tzinfo=pytz.UTC),
            procedure_id=1,
            procedure_name="Blood Test",
            procedure_code="B123",
            order_type="Lab",
            order_status="Completed",
            order_proc_deid="PROC123",
            description="Complete blood count",
            comp_result_name="Hemoglobin",
            ord_value="14.5",
            ord_num_value=14.5,
            reference_low="13.5",
            reference_high="17.5",
            reference_unit="g/dL",
            result_flag="Normal",
            lab_status="Final"
        )

    def test_get_labs_authenticated(self):
        """Test retrieving lab records for authenticated user."""
        self.authenticate_user()
        
        response = self.client.get('/api/v1/research/private/labs/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        # Verify the response contains the created lab
        self.assertEqual(response.data[0]['id'], self.lab.id)

    def test_get_lab_detail_authenticated(self):
        """Test retrieving lab detail for authenticated user."""
        self.authenticate_user()
        
        response = self.client.get(f'/api/v1/research/private/labs/{self.lab.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.lab.id)

    def test_get_labs_unauthorized(self):
        """Test that unauthenticated requests return 401."""
        response = self.client.get('/api/v1/research/private/labs/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_lab_detail_unauthorized(self):
        """Test that unauthenticated detail requests return 401."""
        response = self.client.get(f'/api/v1/research/private/labs/{self.lab.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_lab_detail_not_found(self):
        """Test 404 for non-existent lab ID."""
        self.authenticate_user()
        response = self.client.get('/api/v1/research/private/labs/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)