"""
Tests for VisitOccurrence API endpoints.
Basic CRUD operations with authentication and authorization.
"""
from rest_framework import status
from .test_base import BaseResearchAPITestCase


class VisitOccurrenceAPITest(BaseResearchAPITestCase):
    """Test cases for VisitOccurrence API endpoints."""

    def test_get_visits_authenticated(self):
        """Test retrieving visit occurrences for authenticated user."""
        self.authenticate_user()
        
        response = self.client.get('/api/v1/research/private/visits/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_get_visit_detail_authenticated(self):
        """Test retrieving visit detail for authenticated user."""
        self.authenticate_user()
        
        response = self.client.get(f'/api/v1/research/private/visits/{self.visit.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.visit.id)

    def test_get_visits_unauthorized(self):
        """Test that unauthenticated requests return 401."""
        response = self.client.get('/api/v1/research/private/visits/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_visit_detail_unauthorized(self):
        """Test that unauthenticated detail requests return 401."""
        response = self.client.get(f'/api/v1/research/private/visits/{self.visit.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_visit_detail_not_found(self):
        """Test 404 for non-existent visit ID."""
        self.authenticate_user()
        response = self.client.get('/api/v1/research/private/visits/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)