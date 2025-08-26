from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from model_bakery import baker
from unittest.mock import patch, MagicMock

from research.models import Person, Provider, VisitOccurrence, Concept
from research.api.viewsets.research_viewsets import (
    PersonViewSet, ProviderViewSet, VisitOccurrenceViewSet, ConceptViewSet,
    BaseResearchViewSet
)
from accounts.models import Profile, Tier, Organization


class BaseResearchViewSetTest(TestCase):
    """Test cases for BaseResearchViewSet."""
    
    databases = ['research', 'accounts']
    
    def setUp(self):
        self.viewset = BaseResearchViewSet()
        self.person = baker.make(Person, _using='research')
    
    def test_base_viewset_database_routing(self):
        """Test that BaseResearchViewSet routes queries to research database."""
        # Mock the parent get_queryset method
        with patch.object(BaseResearchViewSet.__bases__[0], 'get_queryset') as mock_get_queryset:
            mock_queryset = MagicMock()
            mock_get_queryset.return_value = mock_queryset
            
            result = self.viewset.get_queryset()
            
            # Should call using('research') on the queryset
            mock_queryset.using.assert_called_once_with('research')
    
    def test_base_viewset_permissions(self):
        """Test that BaseResearchViewSet has correct permission classes."""
        from rest_framework.permissions import IsAuthenticated
        self.assertIn(IsAuthenticated, BaseResearchViewSet.permission_classes)


class ResearchViewSetAPITest(APITestCase):
    """Test cases for Research ViewSet API endpoints."""
    
    databases = ['research', 'accounts']
    
    def setUp(self):
        """Set up test data."""
        # Create organization and tiers
        self.organization = baker.make(Organization, name="Research Institute", _using='accounts')
        self.tier_2 = baker.make(Tier, tier_name="Tier 2", level=2, _using='accounts')
        
        # Create test user
        self.user = baker.make(
            User,
            username='researcher',
            email='researcher@example.com',
            _using='accounts'
        )
        self.user.set_password('testpass123')
        self.user.save(using='accounts')
        
        # Handle Profile creation (may be created by signal)
        try:
            self.profile = self.user.profile
            self.profile.organization = self.organization
            self.profile.tier = self.tier_2
            self.profile.save(using='accounts')
        except Profile.DoesNotExist:
            self.profile = baker.make(
                Profile,
                user=self.user,
                organization=self.organization,
                tier=self.tier_2,
                _using='accounts'
            )
        
        # Create test research data
        self.person = baker.make(
            Person,
            year_of_birth=1990,
            gender_source_value="M",
            gender_source_concept_id=8507,
            race_source_value="White",
            race_source_concept_id=8527,
            ethnicity_source_value="Not Hispanic",
            ethnicity_source_concept_id=38003564,
            _using='research'
        )
        
        self.provider = baker.make(
            Provider,
            year_of_birth=1980,
            gender_source_value="F",
            gender_source_concept_id=8532,
            race_source_value="Asian",
            race_source_concept_id=8515,
            ethnicity_source_value="Not Hispanic",
            ethnicity_source_concept_id=38003564,
            _using='research'
        )
        
        self.visit_occurrence = baker.make(
            VisitOccurrence,
            person_id=self.person,
            provider_id=self.provider,
            visit_start_date="2024-01-15",
            visit_start_time="09:00:00",
            visit_source_value="Outpatient",
            visit_source_id=9202,
            tier_id=2,
            _using='research'
        )
        
        self.concept = baker.make(
            Concept,
            concept_name="Hypertension",
            domain_id="Condition",
            vocabulary_id="SNOMED",
            concept_class_id="Clinical Finding",
            standard_concept="S",
            concept_code="38341003",
            valid_start_date="2024-01-01",
            valid_end_date="2099-12-31",
            invalid_reason=None,
            _using='research'
        )
        
        # Create API client
        self.client = APIClient()
        
    def authenticate_user(self, user=None):
        """Authenticate a user and return tokens."""
        if user is None:
            user = self.user
        
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return refresh.access_token, refresh
    
    def test_person_viewset_list_authenticated(self):
        """Test PersonViewSet list endpoint with authentication."""
        self.authenticate_user()
        
        url = '/api/v1/persons/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['year_of_birth'], 1990)
        self.assertEqual(response.data['results'][0]['gender_source_value'], "M")
    
    def test_person_viewset_list_unauthenticated(self):
        """Test PersonViewSet list endpoint without authentication."""
        url = '/api/v1/persons/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_person_viewset_retrieve_authenticated(self):
        """Test PersonViewSet retrieve endpoint with authentication."""
        self.authenticate_user()
        
        url = f'/api/v1/persons/{self.person.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['year_of_birth'], 1990)
        self.assertEqual(response.data['gender_source_value'], "M")
    
    def test_person_viewset_create_not_allowed(self):
        """Test that PersonViewSet does not allow create operations."""
        self.authenticate_user()
        
        data = {
            'year_of_birth': 1985,
            'gender_source_value': 'F',
            'gender_source_concept_id': 8532,
            'race_source_value': 'Asian',
            'race_source_concept_id': 8515,
            'ethnicity_source_value': 'Not Hispanic',
            'ethnicity_source_concept_id': 38003564
        }
        
        url = '/api/v1/persons/'
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_provider_viewset_list_authenticated(self):
        """Test ProviderViewSet list endpoint with authentication."""
        self.authenticate_user()
        
        url = '/api/v1/providers/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['year_of_birth'], 1980)
        self.assertEqual(response.data['results'][0]['gender_source_value'], "F")
    
    def test_provider_viewset_retrieve_authenticated(self):
        """Test ProviderViewSet retrieve endpoint with authentication."""
        self.authenticate_user()
        
        url = f'/api/v1/providers/{self.provider.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['year_of_birth'], 1980)
        self.assertEqual(response.data['gender_source_value'], "F")
    
    def test_visit_occurrence_viewset_list_authenticated(self):
        """Test VisitOccurrenceViewSet list endpoint with authentication."""
        self.authenticate_user()
        
        url = '/api/v1/visit-occurrences/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['visit_start_date'], "2024-01-15")
        self.assertEqual(response.data['results'][0]['visit_source_value'], "Outpatient")
    
    def test_visit_occurrence_viewset_select_related(self):
        """Test that VisitOccurrenceViewSet uses select_related for performance."""
        viewset = VisitOccurrenceViewSet()
        queryset = viewset.get_queryset()
        
        # Check that the queryset has select_related applied
        self.assertIn('person_id', queryset.query.select_related)
        self.assertIn('provider_id', queryset.query.select_related)
    
    def test_concept_viewset_list_authenticated(self):
        """Test ConceptViewSet list endpoint with authentication."""
        self.authenticate_user()
        
        url = '/api/v1/concepts/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['concept_name'], "Hypertension")
        self.assertEqual(response.data['results'][0]['domain_id'], "Condition")
    
    def test_concept_viewset_retrieve_authenticated(self):
        """Test ConceptViewSet retrieve endpoint with authentication."""
        self.authenticate_user()
        
        url = f'/api/v1/concepts/{self.concept.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['concept_name'], "Hypertension")
        self.assertEqual(response.data['domain_id'], "Condition")
    
    def test_viewsets_database_routing(self):
        """Test that all viewsets use the research database."""
        viewsets = [PersonViewSet, ProviderViewSet, VisitOccurrenceViewSet, ConceptViewSet]
        
        for viewset_class in viewsets:
            viewset = viewset_class()
            queryset = viewset.get_queryset()
            
            # Should use research database
            self.assertEqual(queryset.db, 'research')
    
    def test_viewsets_read_only_behavior(self):
        """Test that all viewsets are read-only (no create, update, delete)."""
        self.authenticate_user()
        
        endpoints = [
            ('/api/v1/persons/', {}),
            ('/api/v1/providers/', {}),
            ('/api/v1/visit-occurrences/', {}),
            ('/api/v1/concepts/', {})
        ]
        
        for url, data in endpoints:
            # Test POST (create) - should be not allowed
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
            
            # Test PUT (update) - should be not allowed for detail views
            if url.endswith('/'):
                detail_url = f"{url}1/"
                response = self.client.put(detail_url, data)
                # May be 404 if object doesn't exist, but should not be 200/201
                self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_405_METHOD_NOT_ALLOWED])
                
                # Test DELETE - should be not allowed for detail views
                response = self.client.delete(detail_url)
                self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_405_METHOD_NOT_ALLOWED])