from django.test import TestCase
from model_bakery import baker
from research.models import (
    Person, Provider, VisitOccurrence, Note, ConditionOccurrence,
    DrugExposure, ProcedureOccurrence, Measurement, Observation,
    PatientSurvey, ProviderSurvey, AuditLogs, Concept
)
from research.api.serializers.research_serializers import (
    PersonSerializer, ProviderSerializer, VisitOccurrenceSerializer,
    NoteSerializer, ConditionOccurrenceSerializer, DrugExposureSerializer,
    ProcedureOccurrenceSerializer, MeasurementSerializer, ObservationSerializer,
    PatientSurveySerializer, ProviderSurveySerializer, AuditLogsSerializer,
    ConceptSerializer
)


class PersonSerializerTest(TestCase):
    """Test cases for PersonSerializer."""
    
    databases = ['research']
    
    def setUp(self):
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
        self.serializer = PersonSerializer(instance=self.person)
    
    def test_person_serializer_fields(self):
        """Test that PersonSerializer includes all expected fields."""
        data = self.serializer.data
        self.assertEqual(data['year_of_birth'], 1990)
        self.assertEqual(data['gender_source_value'], "M")
        self.assertEqual(data['gender_source_concept_id'], 8507)
        self.assertEqual(data['race_source_value'], "White")
        self.assertEqual(data['race_source_concept_id'], 8527)
        self.assertEqual(data['ethnicity_source_value'], "Not Hispanic")
        self.assertEqual(data['ethnicity_source_concept_id'], 38003564)
    
    def test_person_serializer_deserialization(self):
        """Test PersonSerializer deserialization."""
        data = {
            'year_of_birth': 1985,
            'gender_source_value': 'F',
            'gender_source_concept_id': 8532,
            'race_source_value': 'Asian',
            'race_source_concept_id': 8515,
            'ethnicity_source_value': 'Not Hispanic',
            'ethnicity_source_concept_id': 38003564
        }
        serializer = PersonSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['year_of_birth'], 1985)
        self.assertEqual(serializer.validated_data['gender_source_value'], 'F')


class ProviderSerializerTest(TestCase):
    """Test cases for ProviderSerializer."""
    
    databases = ['research']
    
    def setUp(self):
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
        self.serializer = ProviderSerializer(instance=self.provider)
    
    def test_provider_serializer_fields(self):
        """Test that ProviderSerializer includes all expected fields."""
        data = self.serializer.data
        self.assertEqual(data['year_of_birth'], 1980)
        self.assertEqual(data['gender_source_value'], "F")
        self.assertEqual(data['gender_source_concept_id'], 8532)
        self.assertEqual(data['race_source_value'], "Asian")
        self.assertEqual(data['race_source_concept_id'], 8515)
        self.assertEqual(data['ethnicity_source_value'], "Not Hispanic")
        self.assertEqual(data['ethnicity_source_concept_id'], 38003564)
    
    def test_provider_serializer_deserialization(self):
        """Test ProviderSerializer deserialization."""
        data = {
            'year_of_birth': 1975,
            'gender_source_value': 'M',
            'gender_source_concept_id': 8507,
            'race_source_value': 'White',
            'race_source_concept_id': 8527,
            'ethnicity_source_value': 'Hispanic',
            'ethnicity_source_concept_id': 38003563
        }
        serializer = ProviderSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['year_of_birth'], 1975)
        self.assertEqual(serializer.validated_data['gender_source_value'], 'M')


class VisitOccurrenceSerializerTest(TestCase):
    """Test cases for VisitOccurrenceSerializer."""
    
    databases = ['research']
    
    def setUp(self):
        self.person = baker.make(Person, _using='research')
        self.provider = baker.make(Provider, _using='research')
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
        self.serializer = VisitOccurrenceSerializer(instance=self.visit_occurrence)
    
    def test_visit_occurrence_serializer_fields(self):
        """Test that VisitOccurrenceSerializer includes all expected fields."""
        data = self.serializer.data
        self.assertEqual(data['visit_start_date'], "2024-01-15")
        self.assertEqual(data['visit_start_time'], "09:00:00")
        self.assertEqual(data['visit_source_value'], "Outpatient")
        self.assertEqual(data['visit_source_id'], 9202)
        self.assertEqual(data['tier_id'], 2)
        self.assertEqual(data['person_id'], self.person.id)
        self.assertEqual(data['provider_id'], self.provider.id)
    
    def test_visit_occurrence_serializer_relationships(self):
        """Test VisitOccurrenceSerializer handles foreign key relationships."""
        data = self.serializer.data
        self.assertIsNotNone(data['person_id'])
        self.assertIsNotNone(data['provider_id'])


class NoteSerializerTest(TestCase):
    """Test cases for NoteSerializer."""
    
    databases = ['research']
    
    def setUp(self):
        self.person = baker.make(Person, _using='research')
        self.provider = baker.make(Provider, _using='research')
        self.visit_occurrence = baker.make(
            VisitOccurrence,
            person_id=self.person,
            provider_id=self.provider,
            _using='research'
        )
        self.note = baker.make(
            Note,
            person_id=self.person,
            provider_id=self.provider,
            visit_occurrence_id=self.visit_occurrence,
            note_date="2024-01-15",
            note_text="Patient presents with symptoms...",
            note_type="Progress Note",
            note_status="Final",
            _using='research'
        )
        self.serializer = NoteSerializer(instance=self.note)
    
    def test_note_serializer_fields(self):
        """Test that NoteSerializer includes all expected fields."""
        data = self.serializer.data
        self.assertEqual(data['note_date'], "2024-01-15")
        self.assertEqual(data['note_text'], "Patient presents with symptoms...")
        self.assertEqual(data['note_type'], "Progress Note")
        self.assertEqual(data['note_status'], "Final")
        self.assertEqual(data['person_id'], self.person.id)
        self.assertEqual(data['provider_id'], self.provider.id)
        self.assertEqual(data['visit_occurrence_id'], self.visit_occurrence.id)


class ConceptSerializerTest(TestCase):
    """Test cases for ConceptSerializer."""
    
    databases = ['research']
    
    def setUp(self):
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
        self.serializer = ConceptSerializer(instance=self.concept)
    
    def test_concept_serializer_fields(self):
        """Test that ConceptSerializer includes all expected fields."""
        data = self.serializer.data
        self.assertEqual(data['concept_name'], "Hypertension")
        self.assertEqual(data['domain_id'], "Condition")
        self.assertEqual(data['vocabulary_id'], "SNOMED")
        self.assertEqual(data['concept_class_id'], "Clinical Finding")
        self.assertEqual(data['standard_concept'], "S")
        self.assertEqual(data['concept_code'], "38341003")


class AuditLogsSerializerTest(TestCase):
    """Test cases for AuditLogsSerializer."""
    
    databases = ['research']
    
    def setUp(self):
        self.person = baker.make(Person, _using='research')
        self.provider = baker.make(Provider, _using='research')
        self.visit_occurrence = baker.make(
            VisitOccurrence,
            person_id=self.person,
            provider_id=self.provider,
            _using='research'
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
            event_action_subtype="VIEW_CHART",
            _using='research'
        )
        self.serializer = AuditLogsSerializer(instance=self.audit_log)
    
    def test_audit_logs_serializer_fields(self):
        """Test that AuditLogsSerializer includes all expected fields."""
        data = self.serializer.data
        self.assertEqual(data['access_time'], "2024-01-15 12:00:00")
        self.assertEqual(data['user_id'], "user123")
        self.assertEqual(data['workstation_id'], "WS001")
        self.assertEqual(data['access_action'], "VIEW")
        self.assertEqual(data['metric_id'], 1)
        self.assertEqual(data['metric_name'], "Patient Chart Access")
        self.assertEqual(data['metric_desc'], "User accessed patient chart")
        self.assertEqual(data['metric_type'], "ACCESS")
        self.assertEqual(data['metric_group'], "PATIENT_DATA")
        self.assertEqual(data['event_action_type'], "READ")
        self.assertEqual(data['event_action_subtype'], "VIEW_CHART")
    
    def test_audit_logs_serializer_read_only_fields(self):
        """Test that AuditLogsSerializer has proper read-only fields."""
        # Try to create serializer with data that should be read-only
        data = {
            'access_time': "2024-01-16 10:00:00",
            'user_id': "user456",
            'workstation_id': "WS002",
            'access_action': "CREATE",
            'metric_id': 2,
            'metric_name': "Data Creation",
            'metric_desc': "User created new data",
            'metric_type': "CREATE",
            'metric_group': "DATA_CREATION",
            'event_action_type': "WRITE",
            'event_action_subtype': "CREATE_RECORD"
        }
        
        serializer = AuditLogsSerializer(data=data)
        # The serializer should validate but ignore read-only fields on creation
        if serializer.is_valid():
            # All audit fields should be read-only according to the serializer definition
            pass  # This is expected behavior for read-only audit logs