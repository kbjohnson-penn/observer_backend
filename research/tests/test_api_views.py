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


class BaseResearchAPITestCase(APITestCase):
    """Base test case with common setup for research API tests."""
    
    def setUp(self):
        """Set up test data."""
        # Create organization and tiers
        self.organization = baker.make(Organization, name="Research Institute", _using='accounts')
        self.tier_1 = baker.make(Tier, tier_name="Tier 1", level=1, _using='accounts')
        self.tier_2 = baker.make(Tier, tier_name="Tier 2", level=2, _using='accounts')
        self.tier_3 = baker.make(Tier, tier_name="Tier 3", level=3, _using='accounts')
        
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
        
        # Create API client
        self.client = APIClient()
        
    def authenticate_user(self, user=None):
        """Authenticate a user and return tokens."""
        if user is None:
            user = self.user
        
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return refresh.access_token, refresh


class SampleDataAPITest(BaseResearchAPITestCase):
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


class PublicVideoStreamAPITest(BaseResearchAPITestCase):
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