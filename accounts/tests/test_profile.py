from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from model_bakery import baker

from accounts.models import Profile, Tier, Organization
from accounts.api.serializers.profile_serializers import ProfileSerializer
from .base import BaseTestCase

User = get_user_model()


class ProfileAPITest(BaseTestCase):
    """Test cases for profile API endpoints."""
    
    def test_get_profile_authenticated(self):
        """Test retrieving profile for authenticated user."""
        self.authenticate_user()
        url = '/api/v1/accounts/profile/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if response has user data in some form
        if 'user' in response.data:
            self.assertEqual(response.data['user']['username'], 'testuser')
        else:
            # Profile might be returned directly
            self.assertIn('username', str(response.data))
    
    def test_get_profile_unauthenticated(self):
        """Test retrieving profile without authentication."""
        url = '/api/v1/accounts/profile/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_profile(self):
        """Test updating user profile."""
        self.authenticate_user()
        url = '/api/v1/accounts/profile/'
        data = {
            'bio': 'Updated bio',
            'phone_number': '555-123-4567',
            'city': 'Cambridge'
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify the response contains updated data
        self.assertEqual(response.data['bio'], 'Updated bio')
        self.assertEqual(response.data['phone_number'], '555-123-4567')
        self.assertEqual(response.data['city'], 'Cambridge')
    
    def test_update_profile_address(self):
        """Test updating profile address field."""
        self.authenticate_user()
        url = '/api/v1/accounts/profile/'
        data = {
            'address': '789 New Street, Suite 101',
            'city': 'San Francisco',
            'state': 'CA',
            'zip_code': '94102'
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['address'], '789 New Street, Suite 101')
        self.assertEqual(response.data['city'], 'San Francisco')
        self.assertEqual(response.data['state'], 'CA')
        self.assertEqual(response.data['zip_code'], '94102')
    
    def test_update_username(self):
        """Test updating username through profile API."""
        self.authenticate_user()
        url = '/api/v1/accounts/profile/'
        data = {'username': 'newtestuser'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'newtestuser')
        
        # Verify user was updated in database
        self.user.refresh_from_db(using='accounts')
        self.assertEqual(self.user.username, 'newtestuser')
    
    def test_profile_fields_included(self):
        """Test that all expected fields are included in profile response."""
        self.authenticate_user()
        url = '/api/v1/accounts/profile/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        expected_fields = [
            'first_name', 'last_name', 'username', 'email', 'date_of_birth',
            'phone_number', 'address', 'city', 'state', 'country', 'zip_code',
            'bio', 'organization', 'tier', 'date_joined', 'last_login'
        ]
        
        for field in expected_fields:
            self.assertIn(field, response.data, f"Field '{field}' missing from profile response")
    
    def test_readonly_fields_not_updatable(self):
        """Test that read-only fields like first_name, last_name, email cannot be updated."""
        self.authenticate_user()
        url = '/api/v1/accounts/profile/'
        
        # Try to update read-only fields
        data = {
            'first_name': 'NewFirst',
            'last_name': 'NewLast', 
            'email': 'newemail@example.com'
        }
        response = self.client.patch(url, data, format='json')
        
        # Request should succeed but read-only fields shouldn't change
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Original values should be preserved
        self.user.refresh_from_db(using='accounts')
        self.assertNotEqual(self.user.first_name, 'NewFirst')
        self.assertNotEqual(self.user.last_name, 'NewLast')
        self.assertNotEqual(self.user.email, 'newemail@example.com')


class ProfileSerializerTest(TestCase):
    """Test cases for ProfileSerializer."""
    
    databases = ['default', 'accounts']
    
    def setUp(self):
        self.user = User.objects.db_manager('accounts').create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        self.organization = baker.make(Organization, name="Test Org", _using='accounts')
        self.tier = baker.make(Tier, tier_name="Tier Test", level=2, _using='accounts')
        
        # Handle profile creation - check if signal created one or create manually
        try:
            self.profile = self.user.profile
            self.profile.organization = self.organization
            self.profile.tier = self.tier
            self.profile.address_1 = "123 Main St"
            self.profile.address_2 = "Apt 4"
            self.profile.city = "Boston"
            self.profile.save(using='accounts')
        except Profile.DoesNotExist:
            self.profile = baker.make(
                Profile,
                user=self.user,
                organization=self.organization,
                tier=self.tier,
                address_1="123 Main St",
                address_2="Apt 4",
                city="Boston",
                _using='accounts'
            )
    
    def test_profile_serialization(self):
        """Test that profile is serialized correctly."""
        serializer = ProfileSerializer(self.profile)
        data = serializer.data
        
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['first_name'], 'John')
        self.assertEqual(data['last_name'], 'Doe')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['city'], 'Boston')
        self.assertEqual(data['address'], '123 Main St, Apt 4')
        self.assertEqual(data['organization']['name'], 'Test Org')
        self.assertEqual(data['tier']['tier_name'], 'Tier Test')
    
    def test_profile_update_with_address(self):
        """Test updating profile with address field."""
        serializer = ProfileSerializer(self.profile)
        update_data = {
            'address': '456 Oak St, Unit 2B',
            'city': 'Cambridge'
        }
        
        serializer = ProfileSerializer(self.profile, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_profile = serializer.save()
        self.assertEqual(updated_profile.address_1, '456 Oak St')
        self.assertEqual(updated_profile.address_2, 'Unit 2B')
        self.assertEqual(updated_profile.city, 'Cambridge')