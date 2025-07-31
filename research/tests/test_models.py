from django.test import TestCase
from model_bakery import baker
from research.models import (
    VisitOccurrence, Person, Provider, Note, ConditionOccurrence,
    DrugExposure, ProcedureOccurrence, Measurement, Observation,
    PatientSurvey, ProviderSurvey, AuditLogs, Concept
)


class PersonModelTest(TestCase):
    """Test cases for Person model."""
    
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
        self.condition = baker.make(
            ConditionOccurrence,
            visit_occurrence_id=self.visit_occurrence,
            is_primary_dx="Yes",
            condition_source_value="Hypertension",
            condition_concept_id=320128,
            concept_code="I10",
            _using='research'
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
        self.drug_exposure = baker.make(
            DrugExposure,
            visit_occurrence_id=self.visit_occurrence,
            drug_ordering_date="2024-01-15",
            drug_exposure_start_datetime="2024-01-15 09:00:00",
            drug_exposure_end_datetime="2024-01-30 09:00:00",
            description="Lisinopril 10mg daily",
            quantity="30",
            _using='research'
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
        self.procedure = baker.make(
            ProcedureOccurrence,
            visit_occurrence_id=self.visit_occurrence,
            procedure_ordering_date="2024-01-15",
            name="Echocardiogram",
            description="Transthoracic echocardiogram",
            future_or_stand="Current",
            _using='research'
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
        self.measurement = baker.make(
            Measurement,
            visit_occurrence_id=self.visit_occurrence,
            bp_systolic=120,
            bp_diastolic=80,
            phys_bp="120/80",
            weight_lb=150.5,
            height="5'8\"",
            pulse=72,
            phys_spo2=98,
            _using='research'
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
        self.observation = baker.make(
            Observation,
            visit_occurrence_id=self.visit_occurrence,
            file_type="video",
            file_path="/path/to/video.mp4",
            observation_date="2024-01-15",
            _using='research'
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
            overall_satisfaction_scale_2=4.5,
            _using='research'
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
            overall_satisfaction_scale_2=5,
            _using='research'
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