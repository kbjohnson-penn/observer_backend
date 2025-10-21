from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from model_bakery import baker

from accounts.models import Profile, Tier, Organization
from .base import BaseTestCase

User = get_user_model()


class PasswordChangeAPITest(BaseTestCase):
    """Test cases for password change API endpoint."""
    
    def test_password_change_success(self):
        """Test successful password change with valid old password."""
        self.authenticate_user()
        url = '/api/v1/accounts/auth/change-password/'
        data = {
            'old_password': 'testpass123',
            'new_password': 'NewSecurePassword123!',
            'new_password_confirm': 'NewSecurePassword123!'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Password updated successfully.')
        
        # Verify the password was actually changed
        self.user.refresh_from_db(using='accounts')
        self.assertTrue(self.user.check_password('NewSecurePassword123!'))
        self.assertFalse(self.user.check_password('testpass123'))
    
    def test_password_change_wrong_old_password(self):
        """Test password change with incorrect old password."""
        self.authenticate_user()
        url = '/api/v1/accounts/auth/change-password/'
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'NewSecurePassword123!',
            'new_password_confirm': 'NewSecurePassword123!'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('old_password', response.data)
        self.assertEqual(response.data['old_password'], ['Current password is incorrect.'])
    
    def test_password_change_password_mismatch(self):
        """Test password change with mismatched new passwords."""
        self.authenticate_user()
        url = '/api/v1/accounts/auth/change-password/'
        data = {
            'old_password': 'testpass123',
            'new_password': 'NewSecurePassword123!',
            'new_password_confirm': 'DifferentPassword123!'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('new_password_confirm', response.data)
        self.assertEqual(response.data['new_password_confirm'], ['New passwords do not match.'])
    
    def test_password_change_weak_password(self):
        """Test password change with weak new password."""
        self.authenticate_user()
        url = '/api/v1/accounts/auth/change-password/'
        data = {
            'old_password': 'testpass123',
            'new_password': 'weak',  # Too short
            'new_password_confirm': 'weak'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('new_password', response.data)
        # Django's built-in min_length validation message
        self.assertIn('Ensure this field has at least 8 characters.', str(response.data['new_password']))
    
    def test_password_change_unauthenticated(self):
        """Test password change without authentication."""
        url = '/api/v1/accounts/auth/change-password/'
        data = {
            'old_password': 'testpass123',
            'new_password': 'NewSecurePassword123!',
            'new_password_confirm': 'NewSecurePassword123!'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_password_change_missing_fields(self):
        """Test password change with missing required fields."""
        self.authenticate_user()
        url = '/api/v1/accounts/auth/change-password/'
        data = {
            'old_password': 'testpass123'
            # Missing new passwords
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('new_password', response.data)
        self.assertIn('new_password_confirm', response.data)
        self.assertEqual(response.data['new_password'], ['This field is required.'])
        self.assertEqual(response.data['new_password_confirm'], ['This field is required.'])
    
    def test_password_change_rate_limiting(self):
        """Test that password change endpoint is rate limited."""
        # Skip this test as rate limiting interferes with other tests
        # In production, rate limiting is important but in tests it causes issues
        self.skipTest("Rate limiting test skipped to avoid interference with other tests")


class PasswordChangeRateLimitTest(TestCase):
    """Separate test class for rate limiting to avoid interference."""
    
    databases = ['default', 'accounts']
    
    def setUp(self):
        """Set up test data with unique user for rate limit testing."""
        self.client = APIClient()
        self.user = User.objects.db_manager('accounts').create_user(
            username='ratelimituser',
            email='ratelimit@example.com',
            password='testpass123'
        )
        # Create basic profile setup
        self.organization = baker.make(Organization, name="Rate Limit Org", _using='accounts')
        self.tier = baker.make(Tier, tier_name="Tier 2", level=2, _using='accounts')
        
        try:
            self.profile = self.user.profile
            self.profile.organization = self.organization
            self.profile.tier = self.tier
            self.profile.save(using='accounts')
        except Profile.DoesNotExist:
            self.profile = baker.make(
                Profile,
                user=self.user,
                organization=self.organization,
                tier=self.tier,
                _using='accounts'
            )
    
    def authenticate_user(self):
        """Authenticate the test user."""
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return refresh.access_token, refresh
    
    def test_password_change_rate_limit_exceeded(self):
        """Test rate limiting on password change endpoint."""
        self.authenticate_user()
        url = '/api/v1/accounts/auth/change-password/'
        
        # Make multiple requests to trigger rate limit (5 per minute)
        for i in range(6):
            data = {
                'old_password': 'testpass123',
                'new_password': f'NewPassword{i}!',
                'new_password_confirm': f'NewPassword{i}!'
            }
            response = self.client.post(url, data, format='json')
            
            if i < 5:
                # First 5 should either succeed, fail validation, or be rate limited
                self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN])
                if response.status_code == status.HTTP_403_FORBIDDEN:
                    # Rate limit triggered
                    break
            else:
                # 6th request should be rate limited
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                break