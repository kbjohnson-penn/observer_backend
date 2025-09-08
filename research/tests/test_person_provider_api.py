"""
Tests for Person and Provider API endpoints.
Basic CRUD operations with authentication and authorization.
"""
from rest_framework import status
from .test_base import BaseResearchAPITestCase


class PersonAPITest(BaseResearchAPITestCase):
    """Test cases for Person API endpoints."""

    def test_get_persons_authenticated(self):
        """Test retrieving persons for authenticated user."""
        self.authenticate_user()
        
        response = self.client.get('/api/v1/private/persons/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_get_person_detail_authenticated(self):
        """Test retrieving person detail for authenticated user."""
        self.authenticate_user()
        
        response = self.client.get(f'/api/v1/private/persons/{self.person.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.person.id)

    def test_get_persons_unauthorized(self):
        """Test that unauthenticated requests return 401."""
        response = self.client.get('/api/v1/private/persons/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_person_detail_unauthorized(self):
        """Test that unauthenticated detail requests return 401."""
        response = self.client.get(f'/api/v1/private/persons/{self.person.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_person_detail_not_found(self):
        """Test 404 for non-existent person ID."""
        self.authenticate_user()
        response = self.client.get('/api/v1/private/persons/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProviderAPITest(BaseResearchAPITestCase):
    """Test cases for Provider API endpoints."""

    def test_get_providers_authenticated(self):
        """Test retrieving providers for authenticated user."""
        self.authenticate_user()
        
        response = self.client.get('/api/v1/private/research-providers/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_get_provider_detail_authenticated(self):
        """Test retrieving provider detail for authenticated user."""
        self.authenticate_user()
        
        response = self.client.get(f'/api/v1/private/research-providers/{self.provider.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.provider.id)

    def test_get_providers_unauthorized(self):
        """Test that unauthenticated requests return 401."""
        response = self.client.get('/api/v1/private/research-providers/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_provider_detail_unauthorized(self):
        """Test that unauthenticated detail requests return 401."""
        response = self.client.get(f'/api/v1/private/research-providers/{self.provider.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_provider_detail_not_found(self):
        """Test 404 for non-existent provider ID."""
        self.authenticate_user()
        response = self.client.get('/api/v1/private/research-providers/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)