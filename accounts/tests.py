from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from model_bakery import baker
import json

from accounts.models import Profile, Tier, Organization
from accounts.api.serializers.profile_serializers import ProfileSerializer

User = get_user_model()


class BaseTestCase(APITestCase):
    """Base test case with common setup for all account tests."""
    
    def setUp(self):
        """Set up test data."""
        # Create test organization with accounts database
        self.organization = baker.make(Organization, name="Test Hospital", _using='accounts')
        
        # Create test tiers with accounts database (1=lowest access, 5=highest)
        self.tier_1 = baker.make(Tier, tier_name="Tier1", level=1, _using='accounts')  # Lowest access
        self.tier_2 = baker.make(Tier, tier_name="Tier2", level=2, _using='accounts')
        self.tier_3 = baker.make(Tier, tier_name="Tier3", level=3, _using='accounts')
        self.tier_4 = baker.make(Tier, tier_name="Tier4", level=4, _using='accounts')
        self.tier_5 = baker.make(Tier, tier_name="Tier5", level=5, _using='accounts')  # Highest access
        
        # Create test users with accounts database
        self.user = User.objects.using('accounts').create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test profile with accounts database
        self.profile = baker.make(
            Profile,
            user=self.user,
            organization=self.organization,
            tier=self.tier_2,
            _using='accounts'
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


class TierModelTest(TestCase):
    """Test cases for Tier model."""
    
    def setUp(self):
        self.tier = baker.make(Tier, tier_name="TestTier", level=1, _using='accounts')
    
    def test_tier_str_representation(self):
        """Test the string representation of Tier."""
        self.assertEqual(str(self.tier), "TestTier (Level 1)")
    
    def test_tier_ordering(self):
        """Test that tiers are ordered by level (1=lowest, 5=highest)."""
        tier_high = baker.make(Tier, tier_name="HighTier", level=5, _using='accounts')  # Highest access
        tier_low = baker.make(Tier, tier_name="LowTier", level=2, _using='accounts')   # Lower access 
        tier_mid = baker.make(Tier, tier_name="MidTier", level=3, _using='accounts')   # Mid access
        
        tiers = list(Tier.objects.using('accounts').all().order_by('level'))
        # Should be ordered: TestTier(1), LowTier(2), MidTier(3), HighTier(5)
        self.assertEqual(tiers[0], self.tier)  # level 1 from setUp
        self.assertEqual(tiers[1], tier_low)   # level 2
        self.assertEqual(tiers[2], tier_mid)   # level 3
        self.assertEqual(tiers[3], tier_high)  # level 5
    
    def test_tier_unique_constraint(self):
        """Test that tier levels and names are unique."""
        with self.assertRaises(Exception):
            baker.make(Tier, tier_name="AnotherTier", level=1, _using='accounts')  # level 1 already exists
        
        with self.assertRaises(Exception):
            baker.make(Tier, tier_name="TestTier", level=2, _using='accounts')  # tier_name already exists


class OrganizationModelTest(TestCase):
    """Test cases for Organization model."""
    
    def setUp(self):
        self.organization = baker.make(Organization, name="Test Hospital", _using='accounts')
    
    def test_organization_str_representation(self):
        """Test the string representation of Organization."""
        self.assertEqual(str(self.organization), "Test Hospital")
    
    def test_organization_fields(self):
        """Test organization field constraints."""
        self.assertTrue(hasattr(self.organization, 'name'))
        self.assertTrue(hasattr(self.organization, 'address_1'))
        self.assertTrue(hasattr(self.organization, 'phone_number'))


class ProfileModelTest(TestCase):
    """Test cases for Profile model."""
    
    def setUp(self):
        self.user = User.objects.using('accounts').create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.organization = baker.make(Organization, name="Test Hospital", _using='accounts')
        self.tier = baker.make(Tier, tier_name="TestTier", level=2, _using='accounts')
        self.profile = baker.make(
            Profile,
            user=self.user,
            organization=self.organization,
            tier=self.tier,
            _using='accounts'
        )
    
    def test_profile_str_representation(self):
        """Test the string representation of Profile."""
        self.assertEqual(str(self.profile), f"Profile({self.user.username})")
    
    def test_profile_user_relationship(self):
        """Test one-to-one relationship with User."""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.user.profile, self.profile)
    
    def test_profile_organization_relationship(self):
        """Test foreign key relationship with Organization."""
        self.assertEqual(self.profile.organization, self.organization)
    
    def test_profile_tier_relationship(self):
        """Test foreign key relationship with Tier."""
        self.assertEqual(self.profile.tier, self.tier)


class AuthenticationAPITest(BaseTestCase):
    """Test cases for authentication API endpoints."""
    
    def test_user_creation(self):
        """Test user creation functionality."""
        initial_count = User.objects.using('accounts').count()
        User.objects.using('accounts').create_user(
            username='newuser',
            email='newuser@example.com',
            password='newpass123'
        )
        self.assertEqual(User.objects.using('accounts').count(), initial_count + 1)
        self.assertTrue(User.objects.using('accounts').filter(username='newuser').exists())
    
    def test_user_login(self):
        """Test user login endpoint."""
        url = '/api/v1/auth/token/'
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_invalid_login(self):
        """Test login with invalid credentials."""
        url = '/api/v1/auth/token/'
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_refresh(self):
        """Test token refresh endpoint."""
        # First get tokens
        login_url = '/api/v1/auth/token/'
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']
        
        # Test refresh
        refresh_url = '/api/v1/auth/token/refresh/'
        refresh_data = {'refresh': refresh_token}
        response = self.client.post(refresh_url, refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class ProfileAPITest(BaseTestCase):
    """Test cases for profile API endpoints."""
    
    def test_get_profile_authenticated(self):
        """Test retrieving profile for authenticated user."""
        self.authenticate_user()
        url = '/api/v1/profile/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_get_profile_unauthenticated(self):
        """Test retrieving profile without authentication."""
        url = '/api/v1/profile/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_profile(self):
        """Test updating user profile."""
        self.authenticate_user()
        url = '/api/v1/profile/'
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')


class TierPermissionTest(BaseTestCase):
    """Test cases for tier-based permissions."""
    
    def setUp(self):
        super().setUp()
        # Create users with different tier levels (1=lowest, 5=highest access)
        self.user_tier1 = User.objects.using('accounts').create_user(
            username='tier1user',
            email='tier1@example.com',
            password='testpass123'
        )
        self.profile_tier1 = baker.make(
            Profile,
            user=self.user_tier1,
            tier=self.tier_1,  # Level 1 - lowest access
            _using='accounts'
        )
        
        self.user_tier5 = User.objects.using('accounts').create_user(
            username='tier5user',
            email='tier5@example.com',
            password='testpass123'
        )
        self.profile_tier5 = baker.make(
            Profile,
            user=self.user_tier5,
            tier=self.tier_5,  # Level 5 - highest access
            _using='accounts'
        )
    
    def test_tier_level_access(self):
        """Test that users can only access data at their tier level or below."""
        from shared.api.permissions.tier_permissions import filter_queryset_by_user_tier
        
        # Create test data with different tiers
        mock_queryset = Tier.objects.using('accounts').all()
        
        # Test tier 1 user (lowest access) - should only access tier 1
        filtered_tier1 = filter_queryset_by_user_tier(
            mock_queryset, self.user_tier1, "level__lte"
        )
        self.assertEqual(filtered_tier1.count(), 1)  # Only tier 1
        
        # Test tier 5 user (highest access) - should access all tiers 1-5
        filtered_tier5 = filter_queryset_by_user_tier(
            mock_queryset, self.user_tier5, "level__lte"
        )
        self.assertEqual(filtered_tier5.count(), 5)  # All tiers (1,2,3,4,5)
    
    def test_superuser_access(self):
        """Test that superusers have access to all tiers."""
        from shared.api.permissions.tier_permissions import filter_queryset_by_user_tier
        
        # Create superuser
        superuser = User.objects.using('accounts').create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        mock_queryset = Tier.objects.using('accounts').all()
        filtered_admin = filter_queryset_by_user_tier(
            mock_queryset, superuser, "level__lte"
        )
        self.assertEqual(filtered_admin.count(), 5)  # All tiers (1,2,3,4,5)
