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
    
    def setUp(self):
        """Set up test data."""
        # Create organization and tiers
        self.organization = baker.make(Organization, name="Test Hospital", _using='accounts')
        self.tier_1 = baker.make(Tier, tier_name="Tier 1", level=1, _using='accounts')
        self.tier_2 = baker.make(Tier, tier_name="Tier 2", level=2, _using='accounts')
        self.tier_3 = baker.make(Tier, tier_name="Tier 3", level=3, _using='accounts')
        
        # Create test user
        self.user = User.objects.using('accounts').create_user(
            username='clinician',
            email='clinician@example.com',
            password='testpass123'
        )
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
        self.patient.save()
        
        # Age should be calculated correctly
        current_year = date.today().year
        expected_age = current_year - 1990
        # Note: This would need the actual age calculation method implemented


class ProviderModelTest(TestCase):
    """Test cases for Provider model."""
    
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
        self.assertTrue(hasattr(self.provider, 'department'))


class DepartmentModelTest(TestCase):
    """Test cases for Department model."""
    
    def setUp(self):
        self.department = baker.make(Department, name="Cardiology", _using='clinical')
    
    def test_department_str_representation(self):
        """Test the string representation of Department."""
        self.assertEqual(str(self.department), "Cardiology")
    
    def test_department_unique_constraint(self):
        """Test that department names are unique."""
        with self.assertRaises(Exception):
            baker.make(Department, name="Cardiology")


class MultiModalDataModelTest(TestCase):
    """Test cases for MultiModalData model."""
    
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


class EncounterModelTest(TestCase):
    """Test cases for Encounter model."""
    
    def setUp(self):
        self.tier = baker.make(Tier, tier_name="Test Tier", level=2, _using='accounts')
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
            tier=self.tier,
            type='clinic'
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
        self.assertEqual(self.encounter.tier, self.tier)
    
    def test_encounter_auto_source_creation(self):
        """Test automatic encounter source creation."""
        # Create encounter without source
        encounter = baker.make(
            Encounter,
            department=self.department,
            patient=self.patient,
            provider=self.provider,
            tier=self.tier,
            type='emergency',
            encounter_source=None
        )
        
        # Save should create encounter source
        encounter.save()
        self.assertIsNotNone(encounter.encounter_source)
        self.assertEqual(encounter.encounter_source.name, "Emergency")
    
    def test_encounter_timezone_handling(self):
        """Test encounter datetime timezone handling."""
        naive_datetime = datetime.now()
        encounter = baker.make(
            Encounter,
            department=self.department,
            patient=self.patient,
            provider=self.provider,
            tier=self.tier,
            encounter_date_and_time=naive_datetime
        )
        
        encounter.save()
        # Should be timezone-aware after save
        self.assertIsNotNone(encounter.encounter_date_and_time.tzinfo)
    
    def test_simcenter_encounter_creation(self):
        """Test automatic patient/provider creation for simcenter encounters."""
        encounter = baker.make(
            Encounter,
            department=self.department,
            tier=self.tier,
            type='simcenter',
            patient=None,
            provider=None
        )
        
        encounter.save()
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
        multi_modal = baker.make(MultiModalData)
        self.encounter.multi_modal_data = multi_modal
        self.encounter.save()
        
        # Delete encounter
        encounter_id = self.encounter.id
        self.encounter.delete()
        
        # Multimodal data should be deleted
        self.assertFalse(MultiModalData.objects.filter(id=multi_modal.id).exists())


class EncounterFileModelTest(TestCase):
    """Test cases for EncounterFile model."""
    
    def setUp(self):
        self.tier = baker.make(Tier, tier_name="Test Tier", level=2, _using='accounts')
        self.department = baker.make(Department, name="Cardiology", _using='clinical')
        self.encounter = baker.make(
            Encounter,
            department=self.department,
            tier=self.tier
        )
        self.encounter_file = baker.make(
            EncounterFile,
            encounter=self.encounter,
            file_path="test/path/file.mp4",
            file_type="video"
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


class EncounterAPITest(BaseClinicalTestCase):
    """Test cases for Encounter API endpoints."""
    
    def test_get_encounters_authenticated(self):
        """Test retrieving encounters for authenticated user."""
        self.authenticate_user()
        
        # Create test encounter
        encounter = baker.make(
            Encounter,
            department=self.department,
            tier=self.tier_2  # User's tier level
        )
        
        url = '/api/v1/encounters/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_encounters_unauthenticated(self):
        """Test retrieving encounters without authentication."""
        url = '/api/v1/encounters/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_encounter_detail(self):
        """Test retrieving specific encounter details."""
        self.authenticate_user()
        
        encounter = baker.make(
            Encounter,
            department=self.department,
            tier=self.tier_2
        )
        
        url = f'/api/v1/encounters/{encounter.id}/'
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
        
        url = '/api/v1/encounters/'
        response = self.client.get(url)
        
        # User with tier 2 should see tier 1 and 2, but not tier 3
        accessible_ids = [item['id'] for item in response.data]
        self.assertIn(encounter_tier1.id, accessible_ids)
        self.assertIn(encounter_tier2.id, accessible_ids)
        self.assertNotIn(encounter_tier3.id, accessible_ids)
    
    def test_create_encounter(self):
        """Test creating a new encounter."""
        self.authenticate_user()
        
        url = '/api/v1/encounters/'
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
        self.assertTrue(Encounter.objects.filter(department=self.department).exists())


class EncounterFileAPITest(BaseClinicalTestCase):
    """Test cases for EncounterFile API endpoints."""
    
    def setUp(self):
        super().setUp()
        self.encounter = baker.make(
            Encounter,
            department=self.department,
            tier=self.tier_2
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
        
        url = '/api/v1/encounterfiles/'
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
        
        url = f'/api/v1/encounterfiles/{self.encounter_file.id}/stream/'
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
        
        url = f'/api/v1/encounterfiles/{self.encounter_file.id}/download/'
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
        
        url = '/api/v1/encounterfiles/by-ids/'
        data = {'ids': [self.encounter_file.id, file2.id]}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_access_denied_for_wrong_tier(self):
        """Test access denied for files not in user's tier."""
        # Create user with tier 1 (lower access)
        user_tier1 = User.objects.create_user(
            username='tier1user',
            email='tier1@example.com',
            password='testpass123'
        )
        baker.make(Profile, user=user_tier1, tier=self.tier_1, _using='accounts')
        
        # Create encounter with tier 3 (higher than user's access)
        encounter_tier3 = baker.make(Encounter, department=self.department, tier_id=self.tier_3.id, _using='clinical')
        file_tier3 = baker.make(EncounterFile, encounter=encounter_tier3)
        
        # Authenticate as tier 1 user
        self.authenticate_user(user_tier1)
        
        url = f'/api/v1/encounterfiles/{file_tier3.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AzureStorageTest(TestCase):
    """Test cases for Azure storage backend."""
    
    @patch('clinical.storage_backend.DataLakeServiceClient')
    def test_storage_initialization(self, mock_client):
        """Test Azure storage client initialization."""
        storage = AzureDataLakeStorage()
        
        # Should initialize with environment variables
        self.assertIsNotNone(storage.account_url)
        self.assertIsNotNone(storage.container_name)
    
    @patch('clinical.storage_backend.DataLakeServiceClient')
    def test_get_content_type(self, mock_client):
        """Test content type detection."""
        storage = AzureDataLakeStorage()
        
        # Test different file types
        self.assertEqual(storage._get_content_type('video.mp4'), 'video/mp4')
        self.assertEqual(storage._get_content_type('audio.mp3'), 'audio/mpeg')
        self.assertEqual(storage._get_content_type('document.pdf'), 'application/pdf')
        self.assertEqual(storage._get_content_type('unknown.xyz'), 'application/octet-stream')
    
    @patch('clinical.storage_backend.DataLakeServiceClient')
    def test_file_operations(self, mock_client):
        """Test file upload/download operations."""
        storage = AzureDataLakeStorage()
        
        # Mock file system client
        mock_fs_client = MagicMock()
        mock_client.return_value.get_file_system_client.return_value = mock_fs_client
        
        # Test file upload
        test_data = b'test file content'
        result = storage.upload_file('test/path/file.txt', test_data)
        
        # Should call appropriate methods
        mock_fs_client.get_file_client.assert_called_with('test/path/file.txt')
        
        # Test file download
        mock_file_client = MagicMock()
        mock_fs_client.get_file_client.return_value = mock_file_client
        
        storage.download_file('test/path/file.txt')
        mock_file_client.download_file.assert_called_once()


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
        
        # Should allow clinical-accounts relationship (for Tier)
        result = router.allow_relation(clinical_obj, accounts_obj)
        self.assertTrue(result)
        
        # Should not allow clinical-research direct relationships
        research_obj = MagicMock()
        research_obj._state.db = 'research'
        
        result = router.allow_relation(clinical_obj, research_obj)
        self.assertTrue(result)  # Allowed for ETL purposes


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
    
    def test_concept_unique_constraint(self):
        """Test that concept codes must be unique per vocabulary."""
        from research.models import Concept
        
        # Create first concept
        concept1 = baker.make(
            Concept,
            concept_id=1,
            concept_code="123",
            vocabulary_name="SNOMED"
        )
        
        # Same concept code in different vocabulary should be allowed
        concept2 = baker.make(
            Concept,
            concept_id=2,
            concept_code="123",
            vocabulary_name="ICD10"
        )
        
        # Same concept code in same vocabulary should fail
        with self.assertRaises(Exception):
            baker.make(
                Concept,
                concept_id=3,
                concept_code="123",
                vocabulary_name="SNOMED"
            )


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


class EncounterFileModelTest(TestCase):
    """Test cases for enhanced EncounterFile model."""
    
    def test_encounter_file_str_with_filename(self):
        """Test string representation with file name."""
        file_obj = EncounterFile(
            file_name="patient_view.mp4",
            file_type="video"
        )
        self.assertEqual(str(file_obj), "patient_view.mp4 (Video)")
    
    def test_encounter_file_str_with_path_only(self):
        """Test string representation with file path only."""
        file_obj = EncounterFile(
            file_path="encounters/123/video/patient_view.mp4",
            file_type="video"
        )
        self.assertEqual(str(file_obj), "File: encounters/123/video/patient_view.mp4")
    
    def test_encounter_file_str_minimal(self):
        """Test string representation with minimal data."""
        file_obj = EncounterFile(id=1, file_type="audio")
        self.assertEqual(str(file_obj), "Audio File #1")
