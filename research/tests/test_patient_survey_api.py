"""
Tests for PatientSurvey API endpoints.
Basic CRUD operations with authentication and authorization.
"""

from django.utils import timezone

import pytz
from rest_framework import status

from research.models import PatientSurvey, VisitOccurrence

from .test_base import BaseResearchAPITestCase


class PatientSurveyAPITest(BaseResearchAPITestCase):
    """Test cases for PatientSurvey API endpoints."""

    def setUp(self):
        super().setUp()  # Sets up authenticated user, profile, tier, person, and provider
        self.visit = VisitOccurrence.objects.using("research").create(
            tier_id=self.tier.id, person=self.person, provider=self.provider, visit_source_id=1
        )
        self.patient_survey = PatientSurvey.objects.using("research").create(
            visit_occurrence_id=self.visit.id,
            form_1_timestamp=timezone.datetime(2023, 1, 1, 9, 0, tzinfo=pytz.UTC),
            visit_date="2025-09-16",
            patient_overall_health=3.0,
            patient_mental_emotional_health=2.0,
            patient_age=4.0,
            patient_education=3.0,
            overall_satisfaction_scale_1=2.0,
            overall_satisfaction_scale_2=8.0,
            tech_experience_1=1.0,
            tech_experience_2=1.0,
            relationship_with_provider_1=3.0,
            relationship_with_provider_2=1.0,
            hawthorne_1=1.0,
            hawthorne_2=3.0,
            hawthorne_3=2.0,
            hawthorne_4=0.0,
            visit_related_1=1.0,
            visit_related_2=1.0,
            visit_related_3=1.0,
            visit_related_4=2.0,
            visit_related_5=1.0,
            visit_related_6=1.0,
            hawthorne_5=3.0,
            open_ended_interaction="Listening attentively because it made me feel valued",
            open_ended_change="Shorter wait time",
            open_ended_experience="Satisfactory",
        )

    def test_get_patient_surveys_authenticated(self):
        """Test retrieving patient surveys for authenticated user."""
        self.authenticate_user()

        response = self.client.get("/api/v1/research/private/patient-surveys/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_get_patient_survey_detail_authenticated(self):
        """Test retrieving patient survey detail for authenticated user."""
        self.authenticate_user()

        response = self.client.get(
            f"/api/v1/research/private/patient-surveys/{self.patient_survey.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.patient_survey.id)

    def test_get_patient_surveys_unauthorized(self):
        """Test that unauthenticated requests return 401."""
        response = self.client.get("/api/v1/research/private/patient-surveys/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_patient_survey_detail_unauthorized(self):
        """Test that unauthenticated detail requests return 401."""
        response = self.client.get(
            f"/api/v1/research/private/patient-surveys/{self.patient_survey.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_patient_survey_detail_not_found(self):
        """Test 404 for non-existent patient survey ID."""
        self.authenticate_user()
        response = self.client.get("/api/v1/research/private/patient-surveys/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
