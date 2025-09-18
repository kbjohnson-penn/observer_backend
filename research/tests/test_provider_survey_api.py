"""
Tests for ProviderSurvey API endpoints.
Basic CRUD operations with authentication and authorization.
"""
from rest_framework import status
from django.utils import timezone
import pytz
from .test_base import BaseResearchAPITestCase
from research.models import ProviderSurvey, VisitOccurrence


class ProviderSurveyAPITest(BaseResearchAPITestCase):
    """Test cases for ProviderSurvey API endpoints."""

    def setUp(self):
        super().setUp()  # Sets up authenticated user, profile, tier, person, and provider
        self.visit = VisitOccurrence.objects.using('research').create(
            tier_id=self.tier.id,
            person=self.person,
            provider=self.provider,
            visit_source_id=1
        )
        self.provider_survey = ProviderSurvey.objects.using('research').create(
            visit_occurrence=self.visit,
            form_1_timestamp=timezone.datetime(2023, 1, 1, 9, 0, tzinfo=pytz.UTC),
            visit_date="2023-01-01",
            years_hcp_experience=2,
            tech_experience=4,
            communication_method_1=1,
            communication_method_2=0,
            communication_method_3=0,
            communication_method_4=0,
            communication_method_5=0,
            communication_other="",
            inbasket_messages=3,
            overall_satisfaction_scale_1=2,
            overall_satisfaction_scale_2=8,
            patient_related_1=1,
            patient_related_2=1,
            patient_related_3=1,
            visit_related_1=1,
            visit_related_2=1,
            visit_related_4=1,
            hawthorne_1=3,
            hawthorne_2=3,
            hawthorne_3=3,
            open_ended_1="The patient was very engaged, a great example for trainees.",
            open_ended_2=""
        )

    def test_get_provider_surveys_authenticated(self):
        """Test retrieving provider surveys for authenticated user."""
        self.authenticate_user()
        
        response = self.client.get('/api/v1/research/private/provider-surveys/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_get_provider_survey_detail_authenticated(self):
        """Test retrieving provider survey detail for authenticated user."""
        self.authenticate_user()
        
        response = self.client.get(f'/api/v1/research/private/provider-surveys/{self.provider_survey.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.provider_survey.id)

    def test_get_provider_surveys_unauthorized(self):
        """Test that unauthenticated requests return 401."""
        response = self.client.get('/api/v1/research/private/provider-surveys/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_provider_survey_detail_unauthorized(self):
        """Test that unauthenticated detail requests return 401."""
        response = self.client.get(f'/api/v1/research/private/provider-surveys/{self.provider_survey.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_provider_survey_detail_not_found(self):
        """Test 404 for non-existent provider survey ID."""
        self.authenticate_user()
        response = self.client.get('/api/v1/research/private/provider-surveys/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)