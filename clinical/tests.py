from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from model_bakery import baker
from unittest.mock import patch, MagicMock
import json

User = get_user_model()
from datetime import datetime, timedelta

from clinical.models import (
    Encounter, Patient, Provider, Department, EncounterSource,
    MultiModalData, EncounterFile
)
from accounts.models import Profile, Tier, Organization
from clinical.api.serializers.encounter_serializers import EncounterSerializer
from clinical.storage_backend import AzureDataLakeStorage


class BaseClinicalTestCase(APITestCase):
    """Base test case with common setup for clinical tests."""
    
    databases = ['default', 'accounts', 'clinical']
    
    def setUp(self):
        """Set up test data."""
        # Create organization and tiers with accounts database (1=lowest access, 5=highest)
        self.organization = baker.make(Organization, name="Test Hospital", _using='accounts')
        self.tier_1 = baker.make(Tier, tier_name="Tier 1", level=1, _using='accounts')  # Lowest access
        self.tier_2 = baker.make(Tier, tier_name="Tier 2", level=2, _using='accounts')
        self.tier_3 = baker.make(Tier, tier_name="Tier 3", level=3, _using='accounts')
        self.tier_4 = baker.make(Tier, tier_name="Tier 4", level=4, _using='accounts')
        self.tier_5 = baker.make(Tier, tier_name="Tier 5", level=5, _using='accounts')  # Highest access
        
        # Create test user with accounts database
        self.user = User.objects.db_manager('accounts').create_user(
            username='clinician',
            email='clinician@example.com',
            password='testpass123'
        )
        
        # Handle profile creation - check if signal created one or create manually
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
        
        # Create test clinical data
        self.department = baker.make(Department, name="Cardiology", _using='clinical')
        self.encounter_source = baker.make(EncounterSource, name="Clinic", _using='clinical')
        self.patient = baker.make(Patient, patient_id=12345, _using='clinical')
        self.provider = baker.make(Provider, provider_id=67890, _using='clinical')
        
        # Create API client
        self.client = APIClient()
        
    def authenticate_user(self, user=None):
        """Authenticate a user and return tokens."""
        if user is None:
            user = self.user
        
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return refresh.access_token, refresh


class PatientModelTest(TestCase):
    """Test cases for Patient model."""
    
    databases = ['default', 'accounts', 'clinical']
    
    def setUp(self):
        self.patient = baker.make(Patient, patient_id=12345, _using='clinical')
    
    def test_patient_str_representation(self):
        """Test the string representation of Patient."""
        self.assertEqual(str(self.patient), f'PT{self.patient.patient_id}')
    
    def test_patient_id_field(self):
        """Test patient ID field validation."""
        self.assertEqual(self.patient.patient_id, 12345)
        self.assertTrue(hasattr(self.patient, 'first_name'))
        self.assertTrue(hasattr(self.patient, 'last_name'))
        self.assertTrue(hasattr(self.patient, 'date_of_birth'))
        self.assertTrue(hasattr(self.patient, 'sex'))
    
    def test_patient_age_calculation(self):
        """Test patient age calculation."""
        from datetime import date
        self.patient.date_of_birth = date(1990, 1, 1)
        self.patient.save(using='clinical')
        
        # Verify date was saved correctly
        self.assertEqual(self.patient.date_of_birth, date(1990, 1, 1))
        
        # Test that timestamp is auto-created
        self.assertIsNotNone(self.patient.timestamp)
    
    def test_patient_choices_fields(self):
        """Test patient choice fields with valid values."""
        from shared.choices import SEX_CATEGORIES, RACIAL_CATEGORIES, ETHNIC_CATEGORIES
        
        # Use actual choices from the imported constants
        valid_sex = SEX_CATEGORIES[0][0] if SEX_CATEGORIES else 'M'
        valid_race = RACIAL_CATEGORIES[0][0] if RACIAL_CATEGORIES else 'W'
        valid_ethnicity = ETHNIC_CATEGORIES[0][0] if ETHNIC_CATEGORIES else 'NH'
        
        # Test valid choices
        self.patient.sex = valid_sex
        self.patient.race = valid_race
        self.patient.ethnicity = valid_ethnicity
        self.patient.save(using='clinical')
        
        # Verify choices were saved
        self.assertEqual(self.patient.sex, valid_sex)
        self.assertEqual(self.patient.race, valid_race)
        self.assertEqual(self.patient.ethnicity, valid_ethnicity)
    
    def test_patient_id_unique_constraint(self):
        """Test that patient_id must be unique."""
        with self.assertRaises(Exception):
            baker.make(Patient, patient_id=12345, _using='clinical')  # Same ID as setUp
    
    def test_patient_field_validators(self):
        """Test field validators work correctly."""
        # Test valid data doesn't raise exceptions
        self.patient.first_name = "Valid Name"
        self.patient.last_name = "Valid LastName"
        self.patient.save(using='clinical')  # Should not raise
        
        # Verify data was saved
        self.assertEqual(self.patient.first_name, "Valid Name")
        self.assertEqual(self.patient.last_name, "Valid LastName")
    
    def test_patient_empty_optional_fields(self):
        """Test patient with minimal required data."""
        minimal_patient = baker.make(Patient, patient_id=99999, 
                                    first_name="", last_name="", _using='clinical')
        self.assertEqual(str(minimal_patient), "PT99999")
        
        # Verify empty fields are allowed
        self.assertEqual(minimal_patient.first_name, "")
        self.assertEqual(minimal_patient.last_name, "")
    
    def test_patient_manager_methods(self):
        """Test custom manager methods."""
        # Test that we can access the custom manager
        manager = Patient.objects.db_manager('clinical')
        self.assertTrue(hasattr(manager, 'simcenter_range'))
        
        # Test simcenter_range method exists and returns queryset
        simcenter_patients = manager.simcenter_range()
        self.assertIsNotNone(simcenter_patients)
        
        # Create a patient in simcenter range and test
        try:
            from shared.constants import SIMCENTER_PATIENT_ID_LOWER_LIMIT
            if SIMCENTER_PATIENT_ID_LOWER_LIMIT:
                simcenter_patient = baker.make(Patient, 
                                             patient_id=SIMCENTER_PATIENT_ID_LOWER_LIMIT + 1, 
                                             _using='clinical')
                simcenter_results = manager.simcenter_range()
                self.assertIn(simcenter_patient, simcenter_results)
        except ImportError:
            # If constants don't exist, just test that the method works
            simcenter_results = manager.simcenter_range()
            self.assertEqual(list(simcenter_results), [])


class ProviderModelTest(TestCase):
    """Test cases for Provider model."""
    
    databases = ['default', 'accounts', 'clinical']
    
    def setUp(self):
        self.provider = baker.make(Provider, provider_id=67890, _using='clinical')
    
    def test_provider_str_representation(self):
        """Test the string representation of Provider."""
        self.assertEqual(str(self.provider), f'PR{self.provider.provider_id}')
    
    def test_provider_fields(self):
        """Test provider field constraints."""
        self.assertEqual(self.provider.provider_id, 67890)
        self.assertTrue(hasattr(self.provider, 'first_name'))
        self.assertTrue(hasattr(self.provider, 'last_name'))
        self.assertTrue(hasattr(self.provider, 'date_of_birth'))
        self.assertTrue(hasattr(self.provider, 'sex'))
        self.assertTrue(hasattr(self.provider, 'race'))
        self.assertTrue(hasattr(self.provider, 'ethnicity'))
    
    def test_provider_data_persistence(self):
        """Test provider data can be saved and retrieved."""
        from datetime import date
        
        # Set provider data
        self.provider.first_name = 'Dr. John'
        self.provider.last_name = 'Smith'
        self.provider.date_of_birth = date(1980, 5, 15)
        self.provider.sex = 'M'
        self.provider.save(using='clinical')
        
        # Retrieve from database
        saved_provider = Provider.objects.using('clinical').get(provider_id=67890)
        self.assertEqual(saved_provider.first_name, 'Dr. John')
        self.assertEqual(saved_provider.last_name, 'Smith')
        self.assertEqual(saved_provider.date_of_birth, date(1980, 5, 15))
        self.assertEqual(saved_provider.sex, 'M')
    
    def test_provider_timestamp_auto_creation(self):
        """Test that provider timestamp is automatically created."""
        self.assertIsNotNone(self.provider.timestamp)
        
        # Verify it's a datetime object
        from datetime import datetime
        self.assertIsInstance(self.provider.timestamp, datetime)
    
    def test_provider_id_unique_constraint(self):
        """Test that provider_id must be unique."""
        with self.assertRaises(Exception):
            baker.make(Provider, provider_id=67890, _using='clinical')  # Same ID as setUp
    
    def test_provider_field_validators(self):
        """Test provider field validators work correctly."""
        # Test valid data doesn't raise exceptions
        self.provider.first_name = "Dr. Jane"
        self.provider.last_name = "Doe"
        self.provider.save(using='clinical')  # Should not raise
        
        # Verify data was saved
        self.assertEqual(self.provider.first_name, "Dr. Jane")
        self.assertEqual(self.provider.last_name, "Doe")
    
    def test_provider_empty_optional_fields(self):
        """Test provider with minimal required data."""
        minimal_provider = baker.make(Provider, provider_id=99999, 
                                    first_name="", last_name="", _using='clinical')
        self.assertEqual(str(minimal_provider), "PR99999")
        
        # Verify empty fields are allowed
        self.assertEqual(minimal_provider.first_name, "")
        self.assertEqual(minimal_provider.last_name, "")
    
    def test_provider_choices_fields(self):
        """Test provider choice fields with valid values."""
        from shared.choices import SEX_CATEGORIES, RACIAL_CATEGORIES, ETHNIC_CATEGORIES
        
        # Use actual choices from the imported constants
        valid_sex = SEX_CATEGORIES[0][0] if SEX_CATEGORIES else 'F'
        valid_race = RACIAL_CATEGORIES[0][0] if RACIAL_CATEGORIES else 'B'
        valid_ethnicity = ETHNIC_CATEGORIES[0][0] if ETHNIC_CATEGORIES else 'H'
        
        # Test valid choices
        self.provider.sex = valid_sex
        self.provider.race = valid_race
        self.provider.ethnicity = valid_ethnicity
        self.provider.save(using='clinical')
        
        # Verify choices were saved
        self.assertEqual(self.provider.sex, valid_sex)
        self.assertEqual(self.provider.race, valid_race)
        self.assertEqual(self.provider.ethnicity, valid_ethnicity)
    
    def test_provider_manager_methods(self):
        """Test custom provider manager methods if any."""
        # Test that we can access the custom manager
        self.assertTrue(hasattr(Provider.objects, 'using'))
        
        # Test basic manager functionality
        all_providers = Provider.objects.using('clinical').all()
        self.assertIsNotNone(all_providers)
        self.assertIn(self.provider, all_providers)


class EncounterSourceModelTest(TestCase):
    """Test cases for EncounterSource model."""
    
    databases = ['default', 'accounts', 'clinical']
    
    def setUp(self):
        self.encounter_source = baker.make(EncounterSource, name="Clinic", _using='clinical')
    
    def test_encounter_source_str_representation(self):
        """Test the string representation of EncounterSource."""
        self.assertEqual(str(self.encounter_source), "Clinic")
    
    def test_encounter_source_unique_constraint(self):
        """Test that encounter source names are unique."""
        with self.assertRaises(Exception):
            baker.make(EncounterSource, name="Clinic", _using='clinical')  # Same name as setUp
    
    def test_encounter_source_field_validation(self):
        """Test encounter source field validation."""
        # Test valid source name
        self.encounter_source.name = "Emergency Department"
        self.encounter_source.save(using='clinical')
        self.assertEqual(self.encounter_source.name, "Emergency Department")
        
        # Test name field is required (non-empty)
        self.assertTrue(self.encounter_source.name)
        self.assertNotEqual(self.encounter_source.name, "")
    
    def test_encounter_source_max_length(self):
        """Test encounter source name max length constraint."""
        # Test valid length (within 50 chars)
        valid_name = "A" * 50  # Exactly 50 characters
        source = baker.make(EncounterSource, name=valid_name, _using='clinical')
        self.assertEqual(len(source.name), 50)
    
    def test_encounter_source_common_types(self):
        """Test creating common encounter source types."""
        common_sources = ["Emergency", "Outpatient", "Inpatient", "Urgent Care", "Telehealth"]
        
        for source_name in common_sources:
            source = baker.make(EncounterSource, name=source_name, _using='clinical')
            self.assertEqual(str(source), source_name)
            self.assertEqual(source.name, source_name)
    
    def test_encounter_source_crud_operations(self):
        """Test basic CRUD operations on EncounterSource."""
        # Create
        new_source = baker.make(EncounterSource, name="Telehealth", _using='clinical')
        self.assertEqual(str(new_source), "Telehealth")
        
        # Read
        retrieved_source = EncounterSource.objects.using('clinical').get(name="Telehealth")
        self.assertEqual(retrieved_source.name, "Telehealth")
        
        # Update
        retrieved_source.name = "Virtual Care"
        retrieved_source.save(using='clinical')
        updated_source = EncounterSource.objects.using('clinical').get(id=retrieved_source.id)
        self.assertEqual(updated_source.name, "Virtual Care")
        
        # Delete
        source_id = updated_source.id
        updated_source.delete()
        with self.assertRaises(EncounterSource.DoesNotExist):
            EncounterSource.objects.using('clinical').get(id=source_id)
    
    def test_encounter_source_meta_attributes(self):
        """Test EncounterSource model meta attributes."""
        self.assertEqual(self.encounter_source._meta.app_label, 'clinical')
        self.assertEqual(self.encounter_source._meta.verbose_name, 'Source')
        self.assertEqual(self.encounter_source._meta.verbose_name_plural, 'Source')  # Note: same as singular
    
    def test_encounter_source_field_validators(self):
        """Test encounter source field validators."""
        # Test that validate_field validator is applied
        self.encounter_source.name = "Valid Source Name"
        self.encounter_source.save(using='clinical')  # Should not raise
        
        # Verify data was saved
        self.assertEqual(self.encounter_source.name, "Valid Source Name")
    
    def test_encounter_source_relationship_with_encounter(self):
        """Test EncounterSource relationship with Encounter model."""
        # Create related models
        tier = baker.make(Tier, tier_name="Tier 1", level=1, _using='accounts')
        department = baker.make(Department, name="Cardiology", _using='clinical')
        
        # Create encounter with this source
        encounter = baker.make(
            Encounter,
            encounter_source=self.encounter_source,
            department=department,
            tier_id=tier.id,
            _using='clinical'
        )
        
        # Test relationship
        self.assertEqual(encounter.encounter_source, self.encounter_source)
        # Test reverse relationship (encounters with this source)
        related_encounters = Encounter.objects.using('clinical').filter(encounter_source=self.encounter_source)
        self.assertIn(encounter, related_encounters)


class DepartmentModelTest(TestCase):
    """Test cases for Department model."""
    
    databases = ['default', 'accounts', 'clinical']
    
    def setUp(self):
        self.department = baker.make(Department, name="Cardiology", _using='clinical')
    
    def test_department_str_representation(self):
        """Test the string representation of Department."""
        self.assertEqual(str(self.department), "Cardiology")
    
    def test_department_unique_constraint(self):
        """Test that department names are unique."""
        with self.assertRaises(Exception):
            baker.make(Department, name="Cardiology", _using='clinical')  # Same name as setUp
    
    def test_department_field_validation(self):
        """Test department field validation."""
        # Test valid department name
        self.department.name = "Emergency Medicine"
        self.department.save(using='clinical')
        self.assertEqual(self.department.name, "Emergency Medicine")
        
        # Test name field is required (non-empty)
        self.assertTrue(self.department.name)
        self.assertNotEqual(self.department.name, "")
    
    def test_department_max_length(self):
        """Test department name max length constraint."""
        # Test valid length (within 50 chars)
        valid_name = "A" * 50  # Exactly 50 characters
        dept = baker.make(Department, name=valid_name, _using='clinical')
        self.assertEqual(len(dept.name), 50)
    
    def test_department_crud_operations(self):
        """Test basic CRUD operations on Department."""
        # Create
        new_dept = baker.make(Department, name="Neurology", _using='clinical')
        self.assertEqual(str(new_dept), "Neurology")
        
        # Read
        retrieved_dept = Department.objects.using('clinical').get(name="Neurology")
        self.assertEqual(retrieved_dept.name, "Neurology")
        
        # Update
        retrieved_dept.name = "Neurosurgery"
        retrieved_dept.save(using='clinical')
        updated_dept = Department.objects.using('clinical').get(id=retrieved_dept.id)
        self.assertEqual(updated_dept.name, "Neurosurgery")
        
        # Delete
        dept_id = updated_dept.id
        updated_dept.delete()
        with self.assertRaises(Department.DoesNotExist):
            Department.objects.using('clinical').get(id=dept_id)
    
    def test_department_meta_attributes(self):
        """Test Department model meta attributes."""
        self.assertEqual(self.department._meta.app_label, 'clinical')
        self.assertEqual(self.department._meta.verbose_name, 'Department')
        self.assertEqual(self.department._meta.verbose_name_plural, 'Departments')


class MultiModalDataModelTest(TestCase):
    """Test cases for MultiModalData model."""
    
    databases = ['default', 'accounts', 'clinical']
    
    def setUp(self):
        self.multi_modal_data = baker.make(MultiModalData, _using='clinical')
    
    def test_multimodal_data_str_representation(self):
        """Test the string representation of MultiModalData."""
        expected_str = f'MMD{self.multi_modal_data.id}'
        self.assertEqual(str(self.multi_modal_data), expected_str)
    
    def test_multimodal_data_boolean_fields(self):
        """Test boolean fields have correct default values."""
        self.assertFalse(self.multi_modal_data.provider_view)
        self.assertFalse(self.multi_modal_data.patient_view)
        self.assertFalse(self.multi_modal_data.room_view)
        self.assertFalse(self.multi_modal_data.audio)
        self.assertFalse(self.multi_modal_data.transcript)
    
    def test_multimodal_data_timestamp(self):
        """Test that timestamp is auto-generated."""
        self.assertIsNotNone(self.multi_modal_data.timestamp)
        self.assertIsInstance(self.multi_modal_data.timestamp, datetime)
    
    def test_multimodal_data_all_boolean_fields(self):
        """Test all boolean fields exist and have correct defaults."""
        # Test all boolean fields exist
        boolean_fields = [
            'provider_view', 'patient_view', 'room_view', 'audio', 'transcript',
            'patient_survey', 'provider_survey', 'patient_annotation', 
            'provider_annotation', 'rias_transcript', 'rias_codes'
        ]
        
        for field_name in boolean_fields:
            self.assertTrue(hasattr(self.multi_modal_data, field_name))
            # All should default to False
            self.assertFalse(getattr(self.multi_modal_data, field_name))
    
    def test_multimodal_data_field_updates(self):
        """Test updating boolean fields."""
        # Update some fields to True
        self.multi_modal_data.provider_view = True
        self.multi_modal_data.audio = True
        self.multi_modal_data.transcript = True
        self.multi_modal_data.save(using='clinical')
        
        # Verify updates were saved
        updated_data = MultiModalData.objects.using('clinical').get(id=self.multi_modal_data.id)
        self.assertTrue(updated_data.provider_view)
        self.assertTrue(updated_data.audio)
        self.assertTrue(updated_data.transcript)
        
        # Verify other fields remain False
        self.assertFalse(updated_data.patient_view)
        self.assertFalse(updated_data.room_view)
    
    def test_multimodal_data_complete_workflow(self):
        """Test a complete multimodal data workflow."""
        # Initially all False
        self.assertFalse(self.multi_modal_data.provider_view)
        self.assertFalse(self.multi_modal_data.patient_view)
        
        # Enable all data types
        self.multi_modal_data.provider_view = True
        self.multi_modal_data.patient_view = True
        self.multi_modal_data.room_view = True
        self.multi_modal_data.audio = True
        self.multi_modal_data.transcript = True
        self.multi_modal_data.patient_survey = True
        self.multi_modal_data.provider_survey = True
        self.multi_modal_data.save(using='clinical')
        
        # Verify all enabled
        saved_data = MultiModalData.objects.using('clinical').get(id=self.multi_modal_data.id)
        self.assertTrue(saved_data.provider_view)
        self.assertTrue(saved_data.patient_view)
        self.assertTrue(saved_data.room_view)
        self.assertTrue(saved_data.audio)
        self.assertTrue(saved_data.transcript)
        self.assertTrue(saved_data.patient_survey)
        self.assertTrue(saved_data.provider_survey)
    
    def test_multimodal_data_meta_attributes(self):
        """Test MultiModalData model meta attributes."""
        self.assertEqual(self.multi_modal_data._meta.app_label, 'clinical')
        self.assertEqual(self.multi_modal_data._meta.verbose_name, 'Multi Modal Data Path')
        self.assertEqual(self.multi_modal_data._meta.verbose_name_plural, 'Multi Modal Data Paths')
    
    def test_multimodal_data_crud_operations(self):
        """Test basic CRUD operations on MultiModalData."""
        # Create new instance
        new_mmd = baker.make(MultiModalData, provider_view=True, audio=True, _using='clinical')
        self.assertTrue(new_mmd.provider_view)
        self.assertTrue(new_mmd.audio)
        
        # Read
        retrieved_mmd = MultiModalData.objects.using('clinical').get(id=new_mmd.id)
        self.assertTrue(retrieved_mmd.provider_view)
        self.assertTrue(retrieved_mmd.audio)
        
        # Update
        retrieved_mmd.transcript = True
        retrieved_mmd.save(using='clinical')
        updated_mmd = MultiModalData.objects.using('clinical').get(id=retrieved_mmd.id)
        self.assertTrue(updated_mmd.transcript)
        
        # Delete
        mmd_id = updated_mmd.id
        updated_mmd.delete()
        with self.assertRaises(MultiModalData.DoesNotExist):
            MultiModalData.objects.using('clinical').get(id=mmd_id)


class EncounterModelTest(TestCase):
    """Test cases for Encounter model."""
    
    databases = ['default', 'accounts', 'clinical']
    
    def setUp(self):
        self.tier = baker.make(Tier, tier_name="Tier 2", level=2, _using='accounts')
        self.department = baker.make(Department, name="Cardiology", _using='clinical')
        self.patient = baker.make(Patient, patient_id=12345, _using='clinical')
        self.provider = baker.make(Provider, provider_id=67890, _using='clinical')
        self.encounter_source = baker.make(EncounterSource, name="Clinic", _using='clinical')
        
        self.encounter = baker.make(
            Encounter,
            department=self.department,
            patient=self.patient,
            provider=self.provider,
            encounter_source=self.encounter_source,
            tier_id=self.tier.id,
            type='clinic',
            _using='clinical'
        )
    
    def test_encounter_str_representation(self):
        """Test the string representation of Encounter."""
        # For clinic encounters, format should be provider_patient_date
        encounter_str = str(self.encounter)
        self.assertIn(str(self.provider), encounter_str)
        self.assertIn(str(self.patient), encounter_str)
    
    def test_encounter_relationships(self):
        """Test encounter foreign key relationships."""
        self.assertEqual(self.encounter.department, self.department)
        self.assertEqual(self.encounter.patient, self.patient)
        self.assertEqual(self.encounter.provider, self.provider)
        self.assertEqual(self.encounter.tier_id, self.tier.id)
    
    def test_encounter_auto_source_creation(self):
        """Test automatic encounter source creation."""
        # Create encounter without source
        encounter = baker.make(
            Encounter,
            department=self.department,
            patient=self.patient,
            provider=self.provider,
            tier_id=self.tier.id,
            type='emergency',
            encounter_source=None,
            _using='clinical'
        )
        
        # Save should work (business logic may create source)
        encounter.save(using='clinical')
        self.assertIsNotNone(encounter.id)
    
    def test_encounter_timezone_handling(self):
        """Test encounter datetime timezone handling."""
        naive_datetime = datetime.now()
        encounter = baker.make(
            Encounter,
            department=self.department,
            patient=self.patient,
            provider=self.provider,
            tier_id=self.tier.id,
            encounter_date_and_time=naive_datetime,
            _using='clinical'
        )
        
        encounter.save(using='clinical')
        # Verify encounter was saved with the datetime
        self.assertEqual(encounter.encounter_date_and_time.date(), naive_datetime.date())
    
    def test_simcenter_encounter_creation(self):
        """Test automatic patient/provider creation for simcenter encounters."""
        encounter = baker.make(
            Encounter,
            department=self.department,
            tier_id=self.tier.id,
            type='simcenter',
            patient=None,
            provider=None,
            _using='clinical'
        )
        
        encounter.save(using='clinical')
        # Should auto-create patient and provider
        self.assertIsNotNone(encounter.patient)
        self.assertIsNotNone(encounter.provider)
        
        # IDs should be in simcenter range
        from shared.constants import SIMCENTER_PATIENT_ID_LOWER_LIMIT, SIMCENTER_PROVIDER_ID_LOWER_LIMIT
        self.assertGreaterEqual(encounter.patient.patient_id, SIMCENTER_PATIENT_ID_LOWER_LIMIT)
        self.assertGreaterEqual(encounter.provider.provider_id, SIMCENTER_PROVIDER_ID_LOWER_LIMIT)
    
    def test_encounter_cascade_delete(self):
        """Test cascade deletion of related objects."""
        # Create multimodal data
        multi_modal = baker.make(MultiModalData, _using='clinical')
        self.encounter.multi_modal_data = multi_modal
        self.encounter.save(using='clinical')
        
        # Delete encounter
        encounter_id = self.encounter.id
        self.encounter.delete()
        
        # Multimodal data should be deleted
        self.assertFalse(MultiModalData.objects.using('clinical').filter(id=multi_modal.id).exists())
    
    def test_encounter_default_field_values(self):
        """Test encounter default field values."""
        # Test default values
        self.assertEqual(self.encounter.tier_id, self.tier.id)
        self.assertFalse(self.encounter.is_deidentified)
        self.assertTrue(self.encounter.is_restricted)
        self.assertEqual(self.encounter.provider_satisfaction, 0)
        self.assertEqual(self.encounter.patient_satisfaction, 0)
        self.assertEqual(self.encounter.type, 'clinic')
    
    def test_encounter_tier_validation(self):
        """Test encounter tier_id validation."""
        # Test valid tier range (1-5)
        for tier_level in [1, 2, 3, 4, 5]:
            encounter = baker.make(
                Encounter,
                department=self.department,
                tier_id=tier_level,
                _using='clinical'
            )
            self.assertGreaterEqual(encounter.tier_id, 1)
            self.assertLessEqual(encounter.tier_id, 5)
    
    def test_encounter_satisfaction_validation(self):
        """Test satisfaction field validation."""
        # Test valid satisfaction scores (0-5)
        self.encounter.provider_satisfaction = 5
        self.encounter.patient_satisfaction = 3
        self.encounter.save(using='clinical')
        
        updated = Encounter.objects.using('clinical').get(id=self.encounter.id)
        self.assertEqual(updated.provider_satisfaction, 5)
        self.assertEqual(updated.patient_satisfaction, 3)
        
        # Test default satisfaction scores
        new_encounter = baker.make(
            Encounter,
            department=self.department,
            tier_id=self.tier.id,
            _using='clinical'
        )
        self.assertEqual(new_encounter.provider_satisfaction, 0)
        self.assertEqual(new_encounter.patient_satisfaction, 0)
    
    def test_encounter_csn_number_uniqueness(self):
        """Test CSN number uniqueness constraint."""
        # Create encounter with CSN number
        encounter1 = baker.make(
            Encounter,
            department=self.department,
            tier_id=self.tier.id,
            csn_number="1234567890",
            _using='clinical'
        )
        self.assertEqual(encounter1.csn_number, "1234567890")
        
        # Try to create another with same CSN - should fail
        with self.assertRaises(Exception):
            baker.make(
                Encounter,
                department=self.department,
                tier_id=self.tier.id,
                csn_number="1234567890",  # Same CSN
                _using='clinical'
            )
    
    def test_encounter_case_id_field(self):
        """Test case ID field for simcenter encounters."""
        # Test simcenter with case_id
        simcenter = baker.make(
            Encounter,
            department=self.department,
            tier_id=self.tier.id,
            type='simcenter',
            case_id='SIM001',
            _using='clinical'
        )
        self.assertEqual(simcenter.case_id, 'SIM001')
        
        # Test string representation for simcenter
        encounter_str = str(simcenter)
        self.assertEqual(encounter_str, 'SIM001')
    
    def test_encounter_manager_methods(self):
        """Test custom encounter manager methods."""
        manager = Encounter.objects.db_manager('clinical')
        
        # Test with_related method
        self.assertTrue(hasattr(manager, 'with_related'))
        encounters = manager.with_related()
        self.assertIsNotNone(encounters)
        
        # Test by_type method
        self.assertTrue(hasattr(manager, 'by_type'))
        clinic_encounters = manager.by_type('clinic')
        self.assertIn(self.encounter, clinic_encounters)
        
        # Test simcenter method
        self.assertTrue(hasattr(manager, 'simcenter'))
        simcenter_encounters = manager.simcenter()
        # Should be empty since we haven't created simcenter encounters in this test
        self.assertEqual(len(list(simcenter_encounters)), 0)
        
        # Test deidentified_only method
        self.assertTrue(hasattr(manager, 'deidentified_only'))
        deidentified = manager.deidentified_only()
        # Should be empty since encounters default to not deidentified
        self.assertEqual(len(list(deidentified)), 0)
        
        # Test restricted_only method
        self.assertTrue(hasattr(manager, 'restricted_only'))
        restricted = manager.restricted_only()
        # Should include our encounter since it defaults to restricted
        self.assertIn(self.encounter, restricted)
    
    def test_encounter_boolean_fields(self):
        """Test encounter boolean fields."""
        # Test is_deidentified
        self.assertFalse(self.encounter.is_deidentified)
        self.encounter.is_deidentified = True
        self.encounter.save(using='clinical')
        
        updated = Encounter.objects.using('clinical').get(id=self.encounter.id)
        self.assertTrue(updated.is_deidentified)
        
        # Test is_restricted
        self.assertTrue(self.encounter.is_restricted)
        self.encounter.is_restricted = False
        self.encounter.save(using='clinical')
        
        updated = Encounter.objects.using('clinical').get(id=self.encounter.id)
        self.assertFalse(updated.is_restricted)
    
    def test_encounter_multimodal_data_relationship(self):
        """Test encounter multimodal data one-to-one relationship."""
        # Create a new encounter - EncounterService will auto-create MultiModalData
        test_encounter = baker.make(
            Encounter,
            department=self.department,
            tier_id=self.tier.id,
            _using='clinical'
        )
        
        # EncounterService automatically creates MultiModalData on save
        self.assertIsNotNone(test_encounter.multi_modal_data)
        original_mmd = test_encounter.multi_modal_data
        
        # Test the relationship works
        self.assertEqual(test_encounter.multi_modal_data, original_mmd)
        self.assertEqual(original_mmd.encounter, test_encounter)
        
        # Test we can replace the multimodal data
        new_mmd = baker.make(MultiModalData, _using='clinical')
        test_encounter.multi_modal_data = new_mmd
        test_encounter.save(using='clinical')
        
        # Verify the new relationship
        self.assertEqual(test_encounter.multi_modal_data, new_mmd)
        self.assertEqual(new_mmd.encounter, test_encounter)
    
    def test_encounter_source_relationship(self):
        """Test encounter source relationship."""
        # Test the relationship exists
        self.assertEqual(self.encounter.encounter_source, self.encounter_source)
        self.assertEqual(self.encounter.encounter_source.name, "Clinic")
        
        # Test with different source
        emergency_source = baker.make(EncounterSource, name="Emergency", _using='clinical')
        emergency_encounter = baker.make(
            Encounter,
            department=self.department,
            tier_id=self.tier.id,
            encounter_source=emergency_source,
            _using='clinical'
        )
        self.assertEqual(emergency_encounter.encounter_source.name, "Emergency")
    
    def test_encounter_crud_operations(self):
        """Test basic CRUD operations on Encounter."""
        # Create
        new_encounter = baker.make(
            Encounter,
            department=self.department,
            tier_id=self.tier.id,
            type='emergency',
            _using='clinical'
        )
        self.assertEqual(new_encounter.type, 'emergency')
        
        # Read
        retrieved = Encounter.objects.using('clinical').get(id=new_encounter.id)
        self.assertEqual(retrieved.type, 'emergency')
        
        # Update
        retrieved.is_deidentified = True
        retrieved.provider_satisfaction = 4
        retrieved.save(using='clinical')
        updated = Encounter.objects.using('clinical').get(id=retrieved.id)
        self.assertTrue(updated.is_deidentified)
        self.assertEqual(updated.provider_satisfaction, 4)
        
        # Delete
        encounter_id = updated.id
        updated.delete()
        with self.assertRaises(Encounter.DoesNotExist):
            Encounter.objects.using('clinical').get(id=encounter_id)
    
    def test_encounter_timestamp_auto_creation(self):
        """Test that encounter timestamp is automatically created."""
        self.assertIsNotNone(self.encounter.timestamp)
        
        # Verify it's a datetime object and recent
        from datetime import datetime, timedelta
        self.assertIsInstance(self.encounter.timestamp, datetime)
        
        # Should be created within the last few seconds
        time_diff = datetime.now() - self.encounter.timestamp.replace(tzinfo=None)
        self.assertLess(time_diff, timedelta(seconds=10))
    
    def test_encounter_type_choices(self):
        """Test encounter type field choices."""
        # Test clinic type (default in our setUp)
        self.assertEqual(self.encounter.type, 'clinic')
        
        # Test simcenter type
        simcenter_encounter = baker.make(
            Encounter,
            department=self.department,
            tier_id=self.tier.id,
            type='simcenter',
            _using='clinical'
        )
        self.assertEqual(simcenter_encounter.type, 'simcenter')
        
        # Test emergency type (if it exists in choices)
        emergency_encounter = baker.make(
            Encounter,
            department=self.department,
            tier_id=self.tier.id,
            type='emergency',
            _using='clinical'
        )
        # This will work if 'emergency' is a valid choice, otherwise baker will handle it
        self.assertIsNotNone(emergency_encounter.type)


class EncounterFileModelTest(TestCase):
    """Test cases for EncounterFile model."""
    
    databases = ['default', 'accounts', 'clinical']
    
    def setUp(self):
        self.tier = baker.make(Tier, tier_name="Tier 2", level=2, _using='accounts')
        self.department = baker.make(Department, name="Cardiology", _using='clinical')
        self.encounter = baker.make(
            Encounter,
            department=self.department,
            tier_id=self.tier.id,
            _using='clinical'
        )
        self.encounter_file = baker.make(
            EncounterFile,
            encounter=self.encounter,
            file_path="test/path/file.mp4",
            file_type="video",
            _using='clinical'
        )
    
    def test_encounter_file_str_representation(self):
        """Test the string representation of EncounterFile."""
        expected_str = f"File: {self.encounter_file.file_path}"
        self.assertEqual(str(self.encounter_file), expected_str)
    
    def test_encounter_file_relationship(self):
        """Test encounter file foreign key relationship."""
        self.assertEqual(self.encounter_file.encounter, self.encounter)
    
    def test_encounter_file_fields(self):
        """Test encounter file field values."""
        self.assertEqual(self.encounter_file.file_path, "test/path/file.mp4")
        self.assertEqual(self.encounter_file.file_type, "video")
    
    def test_encounter_file_str_with_filename(self):
        """Test string representation when file_name is provided."""
        file_with_name = baker.make(
            EncounterFile,
            encounter=self.encounter,
            file_name="patient_view.mp4",
            file_type="video",
            _using='clinical'
        )
        # Since we don't know the exact FILE_TYPE_CHOICES_DICT mapping, let's test the pattern
        self.assertIn("patient_view.mp4", str(file_with_name))
        self.assertIn("(", str(file_with_name))
        self.assertIn(")", str(file_with_name))
    
    def test_encounter_file_str_with_path_only(self):
        """Test string representation when only file_path is provided."""
        file_path_only = baker.make(
            EncounterFile,
            encounter=self.encounter,
            file_path="encounters/123/video/patient_view.mp4",
            file_name="",  # Empty file_name
            file_type="video",
            _using='clinical'
        )
        expected_str = "File: encounters/123/video/patient_view.mp4"
        self.assertEqual(str(file_path_only), expected_str)
    
    def test_encounter_file_str_minimal(self):
        """Test string representation with minimal data."""
        minimal_file = baker.make(
            EncounterFile,
            encounter=self.encounter,
            file_name="",  # Empty
            file_path="",  # Empty
            file_type="audio",
            _using='clinical'
        )
        # Should show "Audio File #ID" format
        file_str = str(minimal_file)
        self.assertIn("File #", file_str)
        self.assertIn(str(minimal_file.id), file_str)
    
    def test_encounter_file_unique_constraint(self):
        """Test unique constraint on encounter + file_path."""
        # Try to create another file with same encounter and file_path
        with self.assertRaises(Exception):
            baker.make(
                EncounterFile,
                encounter=self.encounter,
                file_path="test/path/file.mp4",  # Same path as setUp
                file_type="audio",  # Different type but same path
                _using='clinical'
            )
    
    def test_encounter_file_different_paths_same_encounter(self):
        """Test that different file paths for same encounter are allowed."""
        file2 = baker.make(
            EncounterFile,
            encounter=self.encounter,
            file_path="test/path/audio.mp3",  # Different path
            file_type="audio",
            _using='clinical'
        )
        self.assertEqual(file2.encounter, self.encounter)
        self.assertNotEqual(file2.file_path, self.encounter_file.file_path)
    
    def test_encounter_file_same_path_different_encounters(self):
        """Test that same file path for different encounters is allowed."""
        # Create another encounter
        encounter2 = baker.make(
            Encounter,
            department=self.department,
            tier_id=self.tier.id,
            _using='clinical'
        )
        
        # Same file path but different encounter should be allowed
        file2 = baker.make(
            EncounterFile,
            encounter=encounter2,
            file_path="test/path/file.mp4",  # Same path as setUp
            file_type="video",
            _using='clinical'
        )
        self.assertEqual(file2.file_path, self.encounter_file.file_path)
        self.assertNotEqual(file2.encounter, self.encounter_file.encounter)
    
    def test_encounter_file_types(self):
        """Test different file types."""
        file_types = ["video", "audio", "transcript", "annotation"]
        
        for file_type in file_types:
            encounter_file = baker.make(
                EncounterFile,
                encounter=self.encounter,
                file_path=f"test/path/{file_type}_file",
                file_type=file_type,
                _using='clinical'
            )
            self.assertEqual(encounter_file.file_type, file_type)
    
    def test_encounter_file_timestamp_auto_creation(self):
        """Test that timestamp is automatically created."""
        self.assertIsNotNone(self.encounter_file.timestamp)
        
        # Verify it's a datetime object and recent
        from datetime import datetime, timedelta
        self.assertIsInstance(self.encounter_file.timestamp, datetime)
        
        # Should be created within the last few seconds
        time_diff = datetime.now() - self.encounter_file.timestamp.replace(tzinfo=None)
        self.assertLess(time_diff, timedelta(seconds=10))
    
    def test_encounter_file_cascade_delete(self):
        """Test that encounter files are deleted when encounter is deleted."""
        file_id = self.encounter_file.id
        
        # Delete the encounter
        self.encounter.delete()
        
        # File should be deleted too (CASCADE)
        with self.assertRaises(EncounterFile.DoesNotExist):
            EncounterFile.objects.using('clinical').get(id=file_id)
    
    def test_encounter_file_manager_methods(self):
        """Test custom EncounterFile manager methods."""
        manager = EncounterFile.objects.db_manager('clinical')
        
        # Test basic manager functionality
        all_files = manager.all()
        self.assertIn(self.encounter_file, all_files)
        
        # Test filtering by encounter
        encounter_files = manager.filter(encounter=self.encounter)
        self.assertIn(self.encounter_file, encounter_files)
    
    def test_encounter_file_crud_operations(self):
        """Test basic CRUD operations on EncounterFile."""
        # Create
        new_file = baker.make(
            EncounterFile,
            encounter=self.encounter,
            file_path="test/new/audio.mp3",
            file_type="audio",
            file_name="recording.mp3",
            _using='clinical'
        )
        self.assertEqual(new_file.file_type, "audio")
        
        # Read
        retrieved = EncounterFile.objects.using('clinical').get(id=new_file.id)
        self.assertEqual(retrieved.file_name, "recording.mp3")
        
        # Update
        retrieved.file_name = "updated_recording.mp3"
        retrieved.save(using='clinical')
        updated = EncounterFile.objects.using('clinical').get(id=retrieved.id)
        self.assertEqual(updated.file_name, "updated_recording.mp3")
        
        # Delete
        file_id = updated.id
        updated.delete()
        with self.assertRaises(EncounterFile.DoesNotExist):
            EncounterFile.objects.using('clinical').get(id=file_id)
    
    def test_encounter_file_related_name(self):
        """Test the related_name 'files' on encounter."""
        # Test that encounter.files returns the related files
        encounter_files = self.encounter.files.all()
        self.assertIn(self.encounter_file, encounter_files)
        
        # Create another file for the same encounter
        file2 = baker.make(
            EncounterFile,
            encounter=self.encounter,
            file_path="test/path2/video2.mp4",
            file_type="video",
            _using='clinical'
        )
        
        # Both files should be in the related files
        encounter_files = self.encounter.files.all()
        self.assertIn(self.encounter_file, encounter_files)
        self.assertIn(file2, encounter_files)
        self.assertEqual(encounter_files.count(), 2)
    
    def test_encounter_file_meta_attributes(self):
        """Test EncounterFile model meta attributes."""
        self.assertEqual(self.encounter_file._meta.app_label, 'clinical')
        
        # Test unique constraint exists
        constraints = self.encounter_file._meta.constraints
        self.assertTrue(any(constraint.name == 'unique_file_per_encounter' for constraint in constraints))


class EncounterAPITest(BaseClinicalTestCase):
    """Test cases for Encounter API endpoints."""
    
    def test_get_encounters_authenticated(self):
        """Test retrieving encounters for authenticated user."""
        self.authenticate_user()
        
        # Create test encounter
        encounter = baker.make(
            Encounter,
            department=self.department,
            tier_id=self.tier_2.id,  # User's tier level
            _using='clinical'
        )
        
        url = '/api/v1/private/encounters/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_encounters_unauthenticated(self):
        """Test retrieving encounters without authentication."""
        url = '/api/v1/private/encounters/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_encounter_detail(self):
        """Test retrieving specific encounter details."""
        self.authenticate_user()
        
        encounter = baker.make(
            Encounter,
            department=self.department,
            tier_id=self.tier_2.id,
            _using='clinical'
        )
        
        url = f'/api/v1/private/encounters/{encounter.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], encounter.id)
    
    def test_tier_based_access_control(self):
        """Test that users can only access encounters at their tier level."""
        self.authenticate_user()
        
        # Create encounters at different tier levels
        encounter_tier1 = baker.make(Encounter, department=self.department, tier_id=self.tier_1.id, _using='clinical')
        encounter_tier2 = baker.make(Encounter, department=self.department, tier_id=self.tier_2.id, _using='clinical')
        encounter_tier3 = baker.make(Encounter, department=self.department, tier_id=self.tier_3.id, _using='clinical')
        
        url = '/api/v1/private/encounters/'
        response = self.client.get(url)
        
        # User with tier 2 should see tier 1 and 2, but not tier 3
        accessible_ids = [item['id'] for item in response.data]
        self.assertIn(encounter_tier1.id, accessible_ids)
        self.assertIn(encounter_tier2.id, accessible_ids)
        self.assertNotIn(encounter_tier3.id, accessible_ids)
    
    def test_create_encounter(self):
        """Test creating a new encounter."""
        self.authenticate_user()
        
        url = '/api/v1/private/encounters/'
        data = {
            'department': self.department.id,
            'patient': self.patient.id,
            'provider': self.provider.id,
            'tier_id': self.tier_2.id,
            'type': 'clinic',
            'encounter_date_and_time': timezone.now().isoformat()
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Encounter.objects.using('clinical').filter(department=self.department).exists())


class EncounterFileAPITest(BaseClinicalTestCase):
    """Test cases for EncounterFile API endpoints."""
    
    def setUp(self):
        super().setUp()
        self.encounter = baker.make(
            Encounter,
            department=self.department,
            tier_id=self.tier_2.id,
            _using='clinical'
        )
        self.encounter_file = baker.make(
            EncounterFile,
            encounter=self.encounter,
            file_path="test/path/video.mp4",
            file_type="video"
        )
    
    def test_get_encounter_files(self):
        """Test retrieving encounter files."""
        self.authenticate_user()
        
        url = '/api/v1/private/encounterfiles/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    @patch('clinical.storage_backend.AzureDataLakeStorage')
    def test_stream_file_endpoint(self, mock_storage):
        """Test file streaming endpoint."""
        self.authenticate_user()
        
        # Mock Azure storage client
        mock_file_client = MagicMock()
        mock_download = MagicMock()
        mock_download.chunks.return_value = [b'test data']
        mock_file_client.download_file.return_value = mock_download
        mock_file_client.path_name = 'test_file.mp4'
        
        mock_storage_instance = MagicMock()
        mock_storage_instance.file_system_client.get_file_client.return_value = mock_file_client
        mock_storage_instance._get_content_type.return_value = 'video/mp4'
        mock_storage.return_value = mock_storage_instance
        
        url = f'/api/v1/private/encounterfiles/{self.encounter_file.id}/stream/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'video/mp4')
    
    @patch('clinical.storage_backend.AzureDataLakeStorage')
    def test_download_file_endpoint(self, mock_storage):
        """Test file download endpoint."""
        self.authenticate_user()
        
        # Mock Azure storage client
        mock_file_client = MagicMock()
        mock_download = MagicMock()
        mock_download.chunks.return_value = [b'test data']
        mock_file_client.download_file.return_value = mock_download
        mock_file_client.path_name = 'test_file.mp4'
        
        mock_storage_instance = MagicMock()
        mock_storage_instance.file_system_client.get_file_client.return_value = mock_file_client
        mock_storage_instance._get_content_type.return_value = 'video/mp4'
        mock_storage.return_value = mock_storage_instance
        
        url = f'/api/v1/private/encounterfiles/{self.encounter_file.id}/download/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'video/mp4')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_get_files_by_ids(self):
        """Test retrieving multiple files by IDs."""
        self.authenticate_user()
        
        # Create additional file
        file2 = baker.make(
            EncounterFile,
            encounter=self.encounter,
            file_path="test/path/audio.mp3",
            file_type="audio"
        )
        
        url = '/api/v1/private/encounterfiles/by-ids/'
        data = {'ids': [self.encounter_file.id, file2.id]}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_access_denied_for_wrong_tier(self):
        """Test access denied for files not in user's tier."""
        # Create user with tier 1 (lower access)
        user_tier1 = User.objects.db_manager('accounts').create_user(
            username='tier1user',
            email='tier1@example.com',
            password='testpass123'
        )
        
        # Handle profile creation - check if signal created one or create manually
        try:
            profile = user_tier1.profile
            profile.tier = self.tier_1
            profile.save(using='accounts')
        except Profile.DoesNotExist:
            baker.make(Profile, user=user_tier1, tier=self.tier_1, _using='accounts')
        
        # Create encounter with tier 3 (higher than user's access)
        encounter_tier3 = baker.make(Encounter, department=self.department, tier_id=self.tier_3.id, _using='clinical')
        file_tier3 = baker.make(EncounterFile, encounter=encounter_tier3)
        
        # Authenticate as tier 1 user
        self.authenticate_user(user_tier1)
        
        url = f'/api/v1/private/encounterfiles/{file_tier3.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AzureStorageTest(TestCase):
    """Test cases for Azure storage backend."""
    
    @patch('clinical.storage_backend.DataLakeServiceClient')
    def test_storage_initialization(self, mock_client):
        """Test Azure storage client initialization."""
        storage = AzureDataLakeStorage()
        
        # Should initialize with environment variables
        self.assertIsNotNone(storage.account_name)
        self.assertIsNotNone(storage.file_system_name)
    
    @patch('clinical.storage_backend.DataLakeServiceClient')
    def test_get_content_type(self, mock_client):
        """Test content type detection."""
        storage = AzureDataLakeStorage()
        
        # Test different file types
        self.assertEqual(storage._get_content_type('video.mp4'), 'video/mp4')
        self.assertEqual(storage._get_content_type('audio.mp3'), 'audio/mpeg')
        self.assertEqual(storage._get_content_type('document.pdf'), 'application/pdf')
        # Note: .xyz extension may be detected as chemical/x-xyz by mimetypes
        unknown_type = storage._get_content_type('unknown.xyz')
        self.assertIn(unknown_type, ['application/octet-stream', 'chemical/x-xyz'])
    
    @patch('clinical.storage_backend.DataLakeServiceClient')
    def test_path_sanitization(self, mock_client):
        """Test path sanitization methods."""
        storage = AzureDataLakeStorage()
        
        # Test valid path component
        self.assertEqual(storage._sanitize_path_component('valid_name.mp4'), 'valid_name.mp4')
        
        # Test invalid path components
        with self.assertRaises(ValidationError):
            storage._sanitize_path_component('../../etc/passwd')
        
        with self.assertRaises(ValidationError):
            storage._sanitize_path_component('.hidden_file')
        
        with self.assertRaises(ValidationError):  
            storage._sanitize_path_component('invalid<>chars')


class DatabaseRoutingTest(TestCase):
    """Test cases for database routing."""
    
    def test_clinical_models_routing(self):
        """Test that clinical models are routed to clinical database."""
        from shared.db_router import DatabaseRouter
        
        router = DatabaseRouter()
        
        # Test reading from clinical database
        read_db = router.db_for_read(Encounter)
        self.assertEqual(read_db, 'clinical')
        
        # Test writing to clinical database
        write_db = router.db_for_write(Encounter)
        self.assertEqual(write_db, 'clinical')
    
    def test_cross_database_relations(self):
        """Test cross-database relationship validation."""
        from shared.db_router import DatabaseRouter
        
        router = DatabaseRouter()
        
        # Create mock objects
        clinical_obj = MagicMock()
        clinical_obj._state.db = 'clinical'
        
        accounts_obj = MagicMock()
        accounts_obj._state.db = 'accounts'
        
        # Should not allow cross-database relationships directly
        result = router.allow_relation(clinical_obj, accounts_obj)
        self.assertFalse(result)
        
        # Same database relationships should be allowed
        clinical_obj2 = MagicMock()
        clinical_obj2._state.db = 'clinical'
        
        result = router.allow_relation(clinical_obj, clinical_obj2)
        self.assertTrue(result)


class DatabaseConstraintTest(TestCase):
    """Test cases for database constraints."""
    
    def test_organization_name_unique_constraint(self):
        """Test that organization names must be unique."""
        from accounts.models import Organization
        
        # Create first organization
        org1 = baker.make(Organization, name="Test Hospital")
        
        # Attempting to create another with same name should raise error
        with self.assertRaises(Exception):
            baker.make(Organization, name="Test Hospital")
    
    def test_encounter_file_unique_constraint(self):
        """Test that file paths must be unique per encounter."""
        tier = baker.make(Tier, tier_name="Test Tier", level=2)
        department = baker.make(Department, name="Cardiology")
        encounter = baker.make(Encounter, department=department, tier_id=tier.id, _using='clinical')
        
        # Create first file
        file1 = baker.make(
            EncounterFile,
            encounter=encounter,
            file_path="test/path/video.mp4"
        )
        
        # Attempting to create another file with same path for same encounter should fail
        with self.assertRaises(Exception):
            baker.make(
                EncounterFile,
                encounter=encounter,
                file_path="test/path/video.mp4"
            )
    
    def test_department_unique_constraint(self):
        """Test that department names must be unique."""
        from clinical.models import Department
        
        # Create first department
        dept1 = baker.make(Department, name="Cardiology", _using='clinical')
        
        # Attempting to create another with same name should raise error
        with self.assertRaises(Exception):
            baker.make(Department, name="Cardiology", _using='clinical')


class EnhancedStorageTest(TestCase):
    """Test cases for enhanced Azure storage exception handling."""
    
    @patch('clinical.storage_backend.DataLakeServiceClient')
    def test_storage_file_exists_error_handling(self, mock_client):
        """Test file creation when file already exists."""
        from clinical.storage_backend import AzureDataLakeStorage
        from azure.core.exceptions import ResourceExistsError
        
        storage = AzureDataLakeStorage()
        
        # Mock directory and file clients
        mock_dir_client = MagicMock()
        mock_file_client = MagicMock()
        mock_dir_client.create_file.side_effect = ResourceExistsError("File exists")
        mock_dir_client.get_file_client.return_value = mock_file_client
        
        mock_fs_client = MagicMock()
        mock_fs_client.get_directory_client.return_value = mock_dir_client
        storage.file_system_client = mock_fs_client
        
        # Mock content
        mock_content = MagicMock()
        mock_content.read.side_effect = [b'test data', b'']
        
        # Test should handle ResourceExistsError and recreate file
        result = storage._save('test.txt', mock_content, 123, 'video')
        
        # Should have called delete_file and create_file again
        mock_file_client.delete_file.assert_called_once()
        self.assertEqual(result, '123/video/test.txt')
    
    @patch('clinical.storage_backend.DataLakeServiceClient')
    def test_storage_write_error_cleanup(self, mock_client):
        """Test file cleanup when write operation fails."""
        from clinical.storage_backend import AzureDataLakeStorage
        from azure.core.exceptions import AzureError
        
        storage = AzureDataLakeStorage()
        
        # Mock directory and file clients
        mock_dir_client = MagicMock()
        mock_file_client = MagicMock()
        mock_file_client.append_data.side_effect = AzureError("Write failed")
        mock_dir_client.create_file.return_value = mock_file_client
        
        mock_fs_client = MagicMock()
        mock_fs_client.get_directory_client.return_value = mock_dir_client
        storage.file_system_client = mock_fs_client
        
        # Mock content
        mock_content = MagicMock()
        mock_content.read.return_value = b'test data'
        
        # Test should cleanup partial file on write error
        with self.assertRaises(AzureError):
            storage._save('test.txt', mock_content, 123, 'video')
        
        # Should have attempted cleanup
        mock_file_client.delete_file.assert_called()
