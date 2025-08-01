from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from model_bakery import baker

from accounts.models import Profile, Tier, Organization

User = get_user_model()


class BaseTestCase(APITestCase):
    """Base test case with common setup for all account tests."""
    
    databases = ['default', 'accounts']
    
    def setUp(self):
        """Set up test data."""
        # Create test organization with accounts database
        self.organization = baker.make(Organization, name="Test Hospital", _using='accounts')
        
        # Create test tiers with accounts database (1=lowest access, 5=highest)
        self.tier_1 = baker.make(Tier, tier_name="Tier 1", level=1, _using='accounts')  # Lowest access
        self.tier_2 = baker.make(Tier, tier_name="Tier 2", level=2, _using='accounts')
        self.tier_3 = baker.make(Tier, tier_name="Tier 3", level=3, _using='accounts')
        self.tier_4 = baker.make(Tier, tier_name="Tier 4", level=4, _using='accounts')
        self.tier_5 = baker.make(Tier, tier_name="Tier 5", level=5, _using='accounts')  # Highest access
        
        # Create test users with accounts database
        self.user = User.objects.db_manager('accounts').create_user(
            username='testuser',
            email='test@example.com',
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
        
        # Create API client
        self.client = APIClient()
        
    def authenticate_user(self, user=None):
        """Authenticate a user and return tokens."""
        if user is None:
            user = self.user
        
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return refresh.access_token, refresh