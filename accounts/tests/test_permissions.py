from django.contrib.auth import get_user_model

from model_bakery import baker

from accounts.models import Profile

from .base import BaseTestCase

User = get_user_model()


class TierPermissionTest(BaseTestCase):
    """Test cases for tier-based permissions."""

    def setUp(self):
        super().setUp()
        # Create users with different tier levels (1=lowest, 5=highest access)
        self.user_tier1 = User.objects.db_manager("accounts").create_user(
            username="tier1user", email="tier1@example.com", password="testpass123"
        )
        # Handle profile creation for tier1 user
        try:
            self.profile_tier1 = self.user_tier1.profile
            self.profile_tier1.tier = self.tier_1
            self.profile_tier1.save(using="accounts")
        except Profile.DoesNotExist:
            self.profile_tier1 = baker.make(
                Profile,
                user=self.user_tier1,
                tier=self.tier_1,  # Level 1 - lowest access
                _using="accounts",
            )

        self.user_tier5 = User.objects.db_manager("accounts").create_user(
            username="tier5user", email="tier5@example.com", password="testpass123"
        )
        # Handle profile creation for tier5 user
        try:
            self.profile_tier5 = self.user_tier5.profile
            self.profile_tier5.tier = self.tier_5
            self.profile_tier5.save(using="accounts")
        except Profile.DoesNotExist:
            self.profile_tier5 = baker.make(
                Profile,
                user=self.user_tier5,
                tier=self.tier_5,  # Level 5 - highest access
                _using="accounts",
            )

    def test_tier_level_access(self):
        """Test that users have correct tier levels."""
        # Simple test to verify tier levels are set correctly
        self.assertEqual(self.profile_tier1.tier.level, 1)  # Lowest access
        self.assertEqual(self.profile_tier5.tier.level, 5)  # Highest access
        self.assertTrue(self.profile_tier5.tier.level > self.profile_tier1.tier.level)

    def test_superuser_creation(self):
        """Test that superusers can be created."""
        # Create superuser
        superuser = User.objects.db_manager("accounts").create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )

        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertEqual(superuser.username, "admin")
