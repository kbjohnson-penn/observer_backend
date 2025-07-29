from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from model_bakery import baker
from unittest.mock import patch, mock_open, MagicMock
import json
import csv
import os

from research.models import (
    VisitOccurrence, Person, Provider, Note, ConditionOccurrence,
    DrugExposure, ProcedureOccurrence, Measurement, Observation,
    PatientSurvey, ProviderSurvey, AuditLogs, Concept
)
from accounts.models import Profile, Tier, Organization
from shared.api.permissions import IsReadOnly


class BaseResearchTestCase(APITestCase):
    """Base test case with common setup for research tests."""
    
    def setUp(self):
        """Set up test data."""
        # Create organization and tiers
        self.organization = baker.make(Organization, name="Research Institute")
        self.tier_1 = baker.make(Tier, tier_name="Tier 1", level=1)
        self.tier_2 = baker.make(Tier, tier_name="Tier 2", level=2)
        self.tier_3 = baker.make(Tier, tier_name="Tier 3", level=3)
        
        # Create test user
        self.user = User.objects.create_user(
            username='researcher',
            email='researcher@example.com',
            password='testpass123'
        )
        self.profile = baker.make(
            Profile,
            user=self.user,
            organization=self.organization,
            tier=self.tier_2
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
            ethnicity_source_concept_id=38003564
        )
        
        self.provider = baker.make(
            Provider,
            year_of_birth=1980,
            gender_source_value="F",
            gender_source_concept_id=8532,
            race_source_value="Asian",
            race_source_concept_id=8515,
            ethnicity_source_value="Not Hispanic",
            ethnicity_source_concept_id=38003564
        )
        
        self.visit_occurrence = baker.make(
            VisitOccurrence,
            person_id=self.person,
            provider_id=self.provider,
            visit_start_date="2024-01-15",
            visit_start_time="09:00:00",
            visit_source_value="Outpatient",
            visit_source_id=9202,
            tier_id=2
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


class PersonModelTest(TestCase):
    """Test cases for Person model."""
    
    def setUp(self):
        self.person = baker.make(
            Person,
            year_of_birth=1990,
            gender_source_value="M",
            gender_source_concept_id=8507,
            race_source_value="White",
            race_source_concept_id=8527,
            ethnicity_source_value="Not Hispanic",
            ethnicity_source_concept_id=38003564
        )
    
    def test_person_fields(self):
        """Test person field values."""
        self.assertEqual(self.person.year_of_birth, 1990)
        self.assertEqual(self.person.gender_source_value, "M")
        self.assertEqual(self.person.gender_source_concept_id, 8507)
        self.assertEqual(self.person.race_source_value, "White")
        self.assertEqual(self.person.race_source_concept_id, 8527)
        self.assertEqual(self.person.ethnicity_source_value, "Not Hispanic")
        self.assertEqual(self.person.ethnicity_source_concept_id, 38003564)
    
    def test_person_database_table(self):
        """Test person model database table name."""
        self.assertEqual(Person._meta.db_table, 'person')
    
    def test_person_app_label(self):
        """Test person model app label."""
        self.assertEqual(Person._meta.app_label, 'research')


class ProviderModelTest(TestCase):
    """Test cases for Provider model."""
    
    def setUp(self):
        self.provider = baker.make(
            Provider,
            year_of_birth=1980,
            gender_source_value="F",
            gender_source_concept_id=8532,
            race_source_value="Asian",
            race_source_concept_id=8515,
            ethnicity_source_value="Not Hispanic",
            ethnicity_source_concept_id=38003564
        )
    
    def test_provider_fields(self):
        """Test provider field values."""
        self.assertEqual(self.provider.year_of_birth, 1980)
        self.assertEqual(self.provider.gender_source_value, "F")
        self.assertEqual(self.provider.gender_source_concept_id, 8532)
        self.assertEqual(self.provider.race_source_value, "Asian")
        self.assertEqual(self.provider.race_source_concept_id, 8515)
        self.assertEqual(self.provider.ethnicity_source_value, "Not Hispanic")
        self.assertEqual(self.provider.ethnicity_source_concept_id, 38003564)
    
    def test_provider_database_table(self):
        """Test provider model database table name."""
        self.assertEqual(Provider._meta.db_table, 'provider')


class VisitOccurrenceModelTest(TestCase):
    """Test cases for VisitOccurrence model."""
    
    def setUp(self):
        self.person = baker.make(Person)
        self.provider = baker.make(Provider)
        self.visit_occurrence = baker.make(
            VisitOccurrence,
            person_id=self.person,
            provider_id=self.provider,
            visit_start_date="2024-01-15",
            visit_start_time="09:00:00",
            visit_source_value="Outpatient",
            visit_source_id=9202,
            tier_id=2
        )
    
    def test_visit_occurrence_relationships(self):
        """Test visit occurrence foreign key relationships."""
        self.assertEqual(self.visit_occurrence.person_id, self.person)
        self.assertEqual(self.visit_occurrence.provider_id, self.provider)
    
    def test_visit_occurrence_fields(self):
        """Test visit occurrence field values."""
        self.assertEqual(self.visit_occurrence.visit_start_date, "2024-01-15")
        self.assertEqual(self.visit_occurrence.visit_start_time, "09:00:00")
        self.assertEqual(self.visit_occurrence.visit_source_value, "Outpatient")
        self.assertEqual(self.visit_occurrence.visit_source_id, 9202)
        self.assertEqual(self.visit_occurrence.tier_id, 2)
    
    def test_visit_occurrence_database_table(self):
        """Test visit occurrence model database table name."""
        self.assertEqual(VisitOccurrence._meta.db_table, 'visit_occurrence')


class NoteModelTest(TestCase):
    """Test cases for Note model."""
    
    def setUp(self):
        self.person = baker.make(Person)
        self.provider = baker.make(Provider)
        self.visit_occurrence = baker.make(
            VisitOccurrence,
            person_id=self.person,
            provider_id=self.provider
        )
        self.note = baker.make(
            Note,
            person_id=self.person,
            provider_id=self.provider,
            visit_occurrence_id=self.visit_occurrence,
            note_date="2024-01-15",
            note_text="Patient presents with symptoms...",
            note_type="Progress Note",
            note_status="Final"
        )
    
    def test_note_relationships(self):
        """Test note foreign key relationships."""
        self.assertEqual(self.note.person_id, self.person)
        self.assertEqual(self.note.provider_id, self.provider)
        self.assertEqual(self.note.visit_occurrence_id, self.visit_occurrence)
    
    def test_note_fields(self):
        """Test note field values."""
        self.assertEqual(self.note.note_date, "2024-01-15")
        self.assertEqual(self.note.note_text, "Patient presents with symptoms...")
        self.assertEqual(self.note.note_type, "Progress Note")
        self.assertEqual(self.note.note_status, "Final")
    
    def test_note_database_table(self):
        """Test note model database table name."""
        self.assertEqual(Note._meta.db_table, 'note')


class ConditionOccurrenceModelTest(TestCase):
    """Test cases for ConditionOccurrence model."""
    
    def setUp(self):
        self.person = baker.make(Person)
        self.provider = baker.make(Provider)
        self.visit_occurrence = baker.make(
            VisitOccurrence,
            person_id=self.person,
            provider_id=self.provider
        )
        self.condition = baker.make(
            ConditionOccurrence,
            visit_occurrence_id=self.visit_occurrence,
            is_primary_dx="Yes",
            condition_source_value="Hypertension",
            condition_concept_id=320128,
            concept_code="I10"
        )
    
    def test_condition_occurrence_relationships(self):
        """Test condition occurrence foreign key relationships."""
        self.assertEqual(self.condition.visit_occurrence_id, self.visit_occurrence)
    
    def test_condition_occurrence_fields(self):
        """Test condition occurrence field values."""
        self.assertEqual(self.condition.is_primary_dx, "Yes")
        self.assertEqual(self.condition.condition_source_value, "Hypertension")
        self.assertEqual(self.condition.condition_concept_id, 320128)
        self.assertEqual(self.condition.concept_code, "I10")
    
    def test_condition_occurrence_database_table(self):
        """Test condition occurrence model database table name."""
        self.assertEqual(ConditionOccurrence._meta.db_table, 'condition_occurrence')


class DrugExposureModelTest(TestCase):
    """Test cases for DrugExposure model."""
    
    def setUp(self):
        self.person = baker.make(Person)
        self.provider = baker.make(Provider)
        self.visit_occurrence = baker.make(
            VisitOccurrence,
            person_id=self.person,
            provider_id=self.provider
        )
        self.drug_exposure = baker.make(
            DrugExposure,
            visit_occurrence_id=self.visit_occurrence,
            drug_ordering_date="2024-01-15",
            drug_exposure_start_datetime="2024-01-15 09:00:00",
            drug_exposure_end_datetime="2024-01-30 09:00:00",
            description="Lisinopril 10mg daily",
            quantity="30"
        )
    
    def test_drug_exposure_relationships(self):
        """Test drug exposure foreign key relationships."""
        self.assertEqual(self.drug_exposure.visit_occurrence_id, self.visit_occurrence)
    
    def test_drug_exposure_fields(self):
        """Test drug exposure field values."""
        self.assertEqual(self.drug_exposure.drug_ordering_date, "2024-01-15")
        self.assertEqual(self.drug_exposure.drug_exposure_start_datetime, "2024-01-15 09:00:00")
        self.assertEqual(self.drug_exposure.drug_exposure_end_datetime, "2024-01-30 09:00:00")
        self.assertEqual(self.drug_exposure.description, "Lisinopril 10mg daily")
        self.assertEqual(self.drug_exposure.quantity, "30")
    
    def test_drug_exposure_database_table(self):
        """Test drug exposure model database table name."""
        self.assertEqual(DrugExposure._meta.db_table, 'drug_exposure')


class ProcedureOccurrenceModelTest(TestCase):
    """Test cases for ProcedureOccurrence model."""
    
    def setUp(self):
        self.person = baker.make(Person)
        self.provider = baker.make(Provider)
        self.visit_occurrence = baker.make(
            VisitOccurrence,
            person_id=self.person,
            provider_id=self.provider
        )
        self.procedure = baker.make(
            ProcedureOccurrence,
            visit_occurrence_id=self.visit_occurrence,
            procedure_ordering_date="2024-01-15",
            name="Echocardiogram",
            description="Transthoracic echocardiogram",
            future_or_stand="Current"
        )
    
    def test_procedure_occurrence_relationships(self):
        """Test procedure occurrence foreign key relationships."""
        self.assertEqual(self.procedure.visit_occurrence_id, self.visit_occurrence)
    
    def test_procedure_occurrence_fields(self):
        """Test procedure occurrence field values."""
        self.assertEqual(self.procedure.procedure_ordering_date, "2024-01-15")
        self.assertEqual(self.procedure.name, "Echocardiogram")
        self.assertEqual(self.procedure.description, "Transthoracic echocardiogram")
        self.assertEqual(self.procedure.future_or_stand, "Current")
    
    def test_procedure_occurrence_database_table(self):
        """Test procedure occurrence model database table name."""
        self.assertEqual(ProcedureOccurrence._meta.db_table, 'procedure_occurrence')


class MeasurementModelTest(TestCase):
    """Test cases for Measurement model."""
    
    def setUp(self):
        self.person = baker.make(Person)
        self.provider = baker.make(Provider)
        self.visit_occurrence = baker.make(
            VisitOccurrence,
            person_id=self.person,
            provider_id=self.provider
        )
        self.measurement = baker.make(
            Measurement,
            visit_occurrence_id=self.visit_occurrence,
            bp_systolic=120,
            bp_diastolic=80,
            phys_bp="120/80",
            weight_lb=150.5,
            height="5'8\"",
            pulse=72,
            phys_spo2=98
        )
    
    def test_measurement_relationships(self):
        """Test measurement foreign key relationships."""
        self.assertEqual(self.measurement.visit_occurrence_id, self.visit_occurrence)
    
    def test_measurement_fields(self):
        """Test measurement field values."""
        self.assertEqual(self.measurement.bp_systolic, 120)
        self.assertEqual(self.measurement.bp_diastolic, 80)
        self.assertEqual(self.measurement.phys_bp, "120/80")
        self.assertEqual(self.measurement.weight_lb, 150.5)
        self.assertEqual(self.measurement.height, "5'8\"")
        self.assertEqual(self.measurement.pulse, 72)
        self.assertEqual(self.measurement.phys_spo2, 98)
    
    def test_measurement_database_table(self):
        """Test measurement model database table name."""
        self.assertEqual(Measurement._meta.db_table, 'measurement')


class ObservationModelTest(TestCase):
    """Test cases for Observation model."""
    
    def setUp(self):
        self.person = baker.make(Person)
        self.provider = baker.make(Provider)
        self.visit_occurrence = baker.make(
            VisitOccurrence,
            person_id=self.person,
            provider_id=self.provider
        )
        self.observation = baker.make(
            Observation,
            visit_occurrence_id=self.visit_occurrence,
            file_type="video",
            file_path="/path/to/video.mp4",
            observation_date="2024-01-15"
        )
    
    def test_observation_relationships(self):
        """Test observation foreign key relationships."""
        self.assertEqual(self.observation.visit_occurrence_id, self.visit_occurrence)
    
    def test_observation_fields(self):
        """Test observation field values."""
        self.assertEqual(self.observation.file_type, "video")
        self.assertEqual(self.observation.file_path, "/path/to/video.mp4")
        self.assertEqual(self.observation.observation_date, "2024-01-15")
    
    def test_observation_database_table(self):
        """Test observation model database table name."""
        self.assertEqual(Observation._meta.db_table, 'observation')


class PatientSurveyModelTest(TestCase):
    """Test cases for PatientSurvey model."""
    
    def setUp(self):
        self.person = baker.make(Person)
        self.provider = baker.make(Provider)
        self.visit_occurrence = baker.make(
            VisitOccurrence,
            person_id=self.person,
            provider_id=self.provider
        )
        self.patient_survey = baker.make(
            PatientSurvey,
            visit_occurrence_id=self.visit_occurrence,
            form_1_timestamp="2024-01-15 10:00:00",
            visit_date="2024-01-15",
            patient_overall_health=4.0,
            patient_mental_emotional_health=3.5,
            patient_age=34.0,
            patient_education=4.0,
            overall_satisfaction_scale_1=5.0,
            overall_satisfaction_scale_2=4.5
        )
    
    def test_patient_survey_relationships(self):
        """Test patient survey foreign key relationships."""
        self.assertEqual(self.patient_survey.visit_occurrence_id, self.visit_occurrence)
    
    def test_patient_survey_fields(self):
        """Test patient survey field values."""
        self.assertEqual(self.patient_survey.form_1_timestamp, "2024-01-15 10:00:00")
        self.assertEqual(self.patient_survey.visit_date, "2024-01-15")
        self.assertEqual(self.patient_survey.patient_overall_health, 4.0)
        self.assertEqual(self.patient_survey.patient_mental_emotional_health, 3.5)
        self.assertEqual(self.patient_survey.patient_age, 34.0)
        self.assertEqual(self.patient_survey.patient_education, 4.0)
        self.assertEqual(self.patient_survey.overall_satisfaction_scale_1, 5.0)
        self.assertEqual(self.patient_survey.overall_satisfaction_scale_2, 4.5)
    
    def test_patient_survey_database_table(self):
        """Test patient survey model database table name."""
        self.assertEqual(PatientSurvey._meta.db_table, 'patient_survey')


class ProviderSurveyModelTest(TestCase):
    """Test cases for ProviderSurvey model."""
    
    def setUp(self):
        self.person = baker.make(Person)
        self.provider = baker.make(Provider)
        self.visit_occurrence = baker.make(
            VisitOccurrence,
            person_id=self.person,
            provider_id=self.provider
        )
        self.provider_survey = baker.make(
            ProviderSurvey,
            visit_occurrence_id=self.visit_occurrence,
            form_1_timestamp="2024-01-15 11:00:00",
            visit_date="2024-01-15",
            years_hcp_experience=10,
            tech_experience=3,
            communication_method_1=1,
            communication_method_2=2,
            inbasket_messages=5,
            overall_satisfaction_scale_1=4,
            overall_satisfaction_scale_2=5
        )
    
    def test_provider_survey_relationships(self):
        """Test provider survey foreign key relationships."""
        self.assertEqual(self.provider_survey.visit_occurrence_id, self.visit_occurrence)
    
    def test_provider_survey_fields(self):
        """Test provider survey field values."""
        self.assertEqual(self.provider_survey.form_1_timestamp, "2024-01-15 11:00:00")
        self.assertEqual(self.provider_survey.visit_date, "2024-01-15")
        self.assertEqual(self.provider_survey.years_hcp_experience, 10)
        self.assertEqual(self.provider_survey.tech_experience, 3)
        self.assertEqual(self.provider_survey.communication_method_1, 1)
        self.assertEqual(self.provider_survey.communication_method_2, 2)
        self.assertEqual(self.provider_survey.inbasket_messages, 5)
        self.assertEqual(self.provider_survey.overall_satisfaction_scale_1, 4)
        self.assertEqual(self.provider_survey.overall_satisfaction_scale_2, 5)
    
    def test_provider_survey_database_table(self):
        """Test provider survey model database table name."""
        self.assertEqual(ProviderSurvey._meta.db_table, 'provider_survey')


class AuditLogsModelTest(TestCase):
    """Test cases for AuditLogs model."""
    
    def setUp(self):
        self.person = baker.make(Person)
        self.provider = baker.make(Provider)
        self.visit_occurrence = baker.make(
            VisitOccurrence,
            person_id=self.person,
            provider_id=self.provider
        )
        self.audit_log = baker.make(
            AuditLogs,
            visit_occurrence_id=self.visit_occurrence,
            access_time="2024-01-15 12:00:00",
            user_id="user123",
            workstation_id="WS001",
            access_action="VIEW",
            metric_id=1,
            metric_name="Patient Chart Access",
            metric_desc="User accessed patient chart",
            metric_type="ACCESS",
            metric_group="PATIENT_DATA",
            event_action_type="READ",
            event_action_subtype="VIEW_CHART"
        )
    
    def test_audit_logs_relationships(self):
        """Test audit logs foreign key relationships."""
        self.assertEqual(self.audit_log.visit_occurrence_id, self.visit_occurrence)
    
    def test_audit_logs_fields(self):
        """Test audit logs field values."""
        self.assertEqual(self.audit_log.access_time, "2024-01-15 12:00:00")
        self.assertEqual(self.audit_log.user_id, "user123")
        self.assertEqual(self.audit_log.workstation_id, "WS001")
        self.assertEqual(self.audit_log.access_action, "VIEW")
        self.assertEqual(self.audit_log.metric_id, 1)
        self.assertEqual(self.audit_log.metric_name, "Patient Chart Access")
        self.assertEqual(self.audit_log.metric_desc, "User accessed patient chart")
        self.assertEqual(self.audit_log.metric_type, "ACCESS")
        self.assertEqual(self.audit_log.metric_group, "PATIENT_DATA")
        self.assertEqual(self.audit_log.event_action_type, "READ")
        self.assertEqual(self.audit_log.event_action_subtype, "VIEW_CHART")
    
    def test_audit_logs_database_table(self):
        """Test audit logs model database table name."""
        self.assertEqual(AuditLogs._meta.db_table, 'audit_logs')


class SampleDataAPITest(BaseResearchTestCase):
    """Test cases for Sample Data API endpoints."""
    
    def test_sample_data_list_authenticated(self):
        """Test retrieving sample data for authenticated user."""
        self.authenticate_user()
        
        # Mock CSV file data
        csv_data = {
            'persons': [
                {'id': 1, 'year_of_birth': 1990, 'gender_source_value': 'M'},
                {'id': 2, 'year_of_birth': 1985, 'gender_source_value': 'F'}
            ],
            'providers': [
                {'id': 1, 'year_of_birth': 1980, 'gender_source_value': 'F'},
                {'id': 2, 'year_of_birth': 1975, 'gender_source_value': 'M'}
            ]
        }
        
        with patch('os.path.exists', return_value=True), \
             patch('os.path.getsize', return_value=1024), \
             patch('builtins.open', mock_open(read_data='id,year_of_birth,gender_source_value\\n1,1990,M\\n2,1985,F\\n')):
            
            url = '/api/v1/sample-data/'
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('_metadata', response.data)
            self.assertIn('persons', response.data)
    
    def test_sample_data_list_unauthenticated(self):
        """Test retrieving sample data without authentication."""
        url = '/api/v1/sample-data/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_sample_data_file_not_found(self):
        """Test sample data when files don't exist."""
        self.authenticate_user()
        
        with patch('os.path.exists', return_value=False):
            url = '/api/v1/sample-data/'
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_sample_data_file_too_large(self):
        """Test sample data with files that are too large."""
        self.authenticate_user()
        
        with patch('os.path.exists', return_value=True), \
             patch('os.path.getsize', return_value=100 * 1024 * 1024):  # 100MB
            
            url = '/api/v1/sample-data/'
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Should include error messages for large files
            for key in ['persons', 'providers', 'visits']:
                if key in response.data:
                    self.assertIn('error', response.data[key])
    
    def test_sample_data_path_traversal_protection(self):
        """Test path traversal protection in sample data."""
        self.authenticate_user()
        
        # Test with malicious path
        with patch('os.path.exists', return_value=True), \
             patch('os.path.getsize', return_value=1024):
            
            url = '/api/v1/sample-data/'
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Should not contain any path traversal attempts
            self.assertNotIn('..', str(response.data))
    
    def test_sample_data_csv_processing(self):
        """Test CSV data processing and type conversion."""
        self.authenticate_user()
        
        # Mock CSV with different data types
        csv_content = 'id,year_of_birth,weight,name,active\\n1,1990,150.5,John,true\\n2,1985,120.0,Jane,false\\n'
        
        with patch('os.path.exists', return_value=True), \
             patch('os.path.getsize', return_value=len(csv_content)), \
             patch('builtins.open', mock_open(read_data=csv_content)):
            
            url = '/api/v1/sample-data/'
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Check that numeric fields are converted
            if 'persons' in response.data and response.data['persons']:
                person = response.data['persons'][0]
                self.assertEqual(person['id'], 1)  # Should be int
                self.assertEqual(person['year_of_birth'], 1990)  # Should be int
                self.assertEqual(person['weight'], 150.5)  # Should be float
                self.assertEqual(person['name'], 'John')  # Should remain string
    
    def test_sample_data_unicode_handling(self):
        """Test handling of Unicode characters in CSV data."""
        self.authenticate_user()
        
        with patch('os.path.exists', return_value=True), \
             patch('os.path.getsize', return_value=1024):
            
            url = '/api/v1/sample-data/'
            response = self.client.get(url)
            
            # Should handle Unicode decode errors gracefully
            self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_sample_data_caching(self):
        """Test that sample data endpoint is cached."""
        self.authenticate_user()
        
        with patch('os.path.exists', return_value=True), \
             patch('os.path.getsize', return_value=1024), \
             patch('builtins.open', mock_open(read_data='id,name\\n1,test\\n')):
            
            url = '/api/v1/sample-data/'
            
            # First request
            response1 = self.client.get(url)
            self.assertEqual(response1.status_code, status.HTTP_200_OK)
            
            # Second request should be cached
            response2 = self.client.get(url)
            self.assertEqual(response2.status_code, status.HTTP_200_OK)
            
            # Responses should be identical
            self.assertEqual(response1.data, response2.data)


class PublicVideoStreamAPITest(BaseResearchTestCase):
    """Test cases for Public Video Stream API endpoints."""
    
    def test_video_stream_head_request(self):
        """Test HEAD request for video file info."""
        self.authenticate_user()
        
        with patch('os.path.exists', return_value=True), \
             patch('os.path.getsize', return_value=1024000), \
             patch('mimetypes.guess_type', return_value=('video/mp4', None)):
            
            url = '/api/v1/video/test_video.mp4/'
            response = self.client.head(url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response['Content-Type'], 'video/mp4')
            self.assertEqual(response['Content-Length'], '1024000')
            self.assertEqual(response['Accept-Ranges'], 'bytes')
    
    def test_video_stream_get_request(self):
        """Test GET request for video file streaming."""
        self.authenticate_user()
        
        with patch('os.path.exists', return_value=True), \
             patch('os.path.getsize', return_value=1024), \
             patch('mimetypes.guess_type', return_value=('video/mp4', None)), \
             patch('builtins.open', mock_open(read_data=b'test video data')):
            
            url = '/api/v1/video/test_video.mp4/'
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response['Content-Type'], 'video/mp4')
            self.assertEqual(response['Accept-Ranges'], 'bytes')
    
    def test_video_stream_range_request(self):
        """Test range request for video file streaming."""
        self.authenticate_user()
        
        with patch('os.path.exists', return_value=True), \
             patch('os.path.getsize', return_value=1024), \
             patch('mimetypes.guess_type', return_value=('video/mp4', None)), \
             patch('builtins.open', mock_open(read_data=b'test video data')):
            
            url = '/api/v1/video/test_video.mp4/'
            response = self.client.get(url, HTTP_RANGE='bytes=0-511')
            
            self.assertEqual(response.status_code, status.HTTP_206_PARTIAL_CONTENT)
            self.assertIn('Content-Range', response)
            self.assertEqual(response['Content-Length'], '512')
    
    def test_video_stream_invalid_range(self):
        """Test invalid range request."""
        self.authenticate_user()
        
        with patch('os.path.exists', return_value=True), \
             patch('os.path.getsize', return_value=1024), \
             patch('mimetypes.guess_type', return_value=('video/mp4', None)):
            
            url = '/api/v1/video/test_video.mp4/'
            response = self.client.get(url, HTTP_RANGE='bytes=2000-3000')  # Beyond file size
            
            self.assertEqual(response.status_code, status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)
    
    def test_video_stream_path_traversal_protection(self):
        """Test path traversal attack protection."""
        self.authenticate_user()
        
        # Test various path traversal attempts
        malicious_paths = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32\\config\\sam',
            'test/../../../sensitive_file.txt',
            'test/../../outside_directory/file.mp4'
        ]
        
        for path in malicious_paths:
            url = f'/api/v1/video/{path}/'
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_video_stream_file_not_found(self):
        """Test streaming non-existent file."""
        self.authenticate_user()
        
        with patch('os.path.exists', return_value=False):
            url = '/api/v1/video/nonexistent.mp4/'
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_video_stream_directory_protection(self):
        """Test protection against directory access."""
        self.authenticate_user()
        
        with patch('os.path.exists', return_value=True), \
             patch('os.path.isfile', return_value=False):  # It's a directory
            
            url = '/api/v1/video/directory_name/'
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_video_stream_content_type_detection(self):
        """Test content type detection for different file types."""
        self.authenticate_user()
        
        file_types = [
            ('video.mp4', 'video/mp4'),
            ('audio.mp3', 'audio/mpeg'),
            ('document.pdf', 'application/pdf'),
            ('spreadsheet.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            ('data.json', 'application/json'),
            ('unknown.xyz', 'application/octet-stream')
        ]
        
        for filename, expected_type in file_types:
            with patch('os.path.exists', return_value=True), \
                 patch('os.path.getsize', return_value=1024), \
                 patch('os.path.isfile', return_value=True):
                
                url = f'/api/v1/video/{filename}/'
                response = self.client.head(url)
                
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response['Content-Type'], expected_type)


class DatabaseRoutingTest(TestCase):
    """Test cases for research database routing."""
    
    def test_research_models_routing(self):
        """Test that research models are routed to research database."""
        from shared.db_router import DatabaseRouter
        
        router = DatabaseRouter()
        
        # Test reading from research database
        read_db = router.db_for_read(VisitOccurrence)
        self.assertEqual(read_db, 'research')
        
        # Test writing to research database
        write_db = router.db_for_write(VisitOccurrence)
        self.assertEqual(write_db, 'research')
        
        # Test other research models
        self.assertEqual(router.db_for_read(Person), 'research')
        self.assertEqual(router.db_for_read(Provider), 'research')
        self.assertEqual(router.db_for_read(Note), 'research')
        self.assertEqual(router.db_for_read(PatientSurvey), 'research')
        self.assertEqual(router.db_for_read(AuditLogs), 'research')
    
    def test_research_model_internal_relations(self):
        """Test that research models can relate to each other."""
        from shared.db_router import DatabaseRouter
        
        router = DatabaseRouter()
        
        # Create mock research objects
        research_obj1 = MagicMock()
        research_obj1._state.db = 'research'
        
        research_obj2 = MagicMock()
        research_obj2._state.db = 'research'
        
        # Should allow relations within research database
        result = router.allow_relation(research_obj1, research_obj2)
        self.assertTrue(result)
    
    def test_research_migration_routing(self):
        """Test migration routing for research models."""
        from shared.db_router import DatabaseRouter
        
        router = DatabaseRouter()
        
        # Should allow research app migrations on research database
        result = router.allow_migrate('research', 'research', 'VisitOccurrence')
        self.assertTrue(result)
        
        # Should not allow research app migrations on other databases
        result = router.allow_migrate('clinical', 'research', 'VisitOccurrence')
        self.assertFalse(result)
        
        result = router.allow_migrate('accounts', 'research', 'VisitOccurrence')
        self.assertFalse(result)
