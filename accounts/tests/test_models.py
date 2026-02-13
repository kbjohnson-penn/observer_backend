from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from model_bakery import baker

from accounts.models import Organization, Profile, Tier
from accounts.models.user_models import EmailVerificationToken

User = get_user_model()


class TierModelTest(TestCase):
    """Test cases for Tier model."""

    databases = ["default", "accounts"]

    def setUp(self):
        self.tier = baker.make(Tier, tier_name="Tier Test", level=1, _using="accounts")

    def test_tier_str_representation(self):
        """Test the string representation of Tier."""
        self.assertEqual(str(self.tier), "Tier Test (Level 1)")

    def test_tier_ordering(self):
        """Test that tiers are ordered by level (1=lowest, 5=highest)."""
        tier_high = baker.make(
            Tier, tier_name="Tier 5", level=5, _using="accounts"
        )  # Highest access
        tier_low = baker.make(Tier, tier_name="Tier 2", level=2, _using="accounts")  # Lower access
        tier_mid = baker.make(Tier, tier_name="Tier 3", level=3, _using="accounts")  # Mid access

        tiers = list(Tier.objects.using("accounts").all().order_by("level"))
        # Should be ordered: Tier Test(1), Tier 2(2), Tier 3(3), Tier 5(5)
        self.assertEqual(tiers[0], self.tier)  # level 1 from setUp
        self.assertEqual(tiers[1], tier_low)  # level 2
        self.assertEqual(tiers[2], tier_mid)  # level 3
        self.assertEqual(tiers[3], tier_high)  # level 5

    def test_tier_unique_constraint(self):
        """Test that tier levels and names are unique."""
        with self.assertRaises(Exception):
            baker.make(
                Tier, tier_name="Tier 6", level=1, _using="accounts"
            )  # level 1 already exists

        with self.assertRaises(Exception):
            baker.make(
                Tier, tier_name="Tier Test", level=2, _using="accounts"
            )  # tier_name already exists


class TierModelExtendedTest(TestCase):
    """Extended test cases for Tier model fields."""

    databases = ["default", "accounts"]

    def setUp(self):
        self.tier = baker.make(
            Tier,
            tier_name="Tier 3",
            level=3,
            complete_deidentification=True,
            blur_sexually_explicit_body_parts=True,
            blur_face=False,
            obscure_voice=True,
            dua=False,
            external_access=True,
            _using="accounts",
        )

    def test_tier_boolean_fields(self):
        """Test that all boolean fields are set correctly."""
        self.assertTrue(self.tier.complete_deidentification)
        self.assertTrue(self.tier.blur_sexually_explicit_body_parts)
        self.assertFalse(self.tier.blur_face)
        self.assertTrue(self.tier.obscure_voice)
        self.assertFalse(self.tier.dua)
        self.assertTrue(self.tier.external_access)

    def test_tier_default_values(self):
        """Test that boolean fields have correct default values."""
        tier = Tier.objects.using("accounts").create(tier_name="Tier 4", level=4)

        # All boolean fields should default to False
        self.assertFalse(tier.complete_deidentification)
        self.assertFalse(tier.blur_sexually_explicit_body_parts)
        self.assertFalse(tier.blur_face)
        self.assertFalse(tier.obscure_voice)
        self.assertFalse(tier.dua)
        self.assertFalse(tier.external_access)


class OrganizationModelTest(TestCase):
    """Test cases for Organization model."""

    databases = ["default", "accounts"]

    def setUp(self):
        self.organization = baker.make(Organization, name="Test Hospital", _using="accounts")

    def test_organization_str_representation(self):
        """Test the string representation of Organization."""
        self.assertEqual(str(self.organization), "Test Hospital")

    def test_organization_fields(self):
        """Test organization field constraints."""
        self.assertTrue(hasattr(self.organization, "name"))
        self.assertTrue(hasattr(self.organization, "address_1"))
        self.assertTrue(hasattr(self.organization, "phone_number"))


class OrganizationModelExtendedTest(TestCase):
    """Extended test cases for Organization model."""

    databases = ["default", "accounts"]

    def test_organization_with_website(self):
        """Test organization with website field."""
        org = Organization.objects.using("accounts").create(
            name="Test Org with Website", website="https://example.com"
        )
        self.assertEqual(org.website, "https://example.com")

    def test_organization_full_address(self):
        """Test organization with full address."""
        org = Organization.objects.using("accounts").create(
            name="Full Address Org",
            address_1="123 Hospital Ave",
            address_2="Suite 100",
            city="Boston",
            state="MA",
            country="US",
            zip_code="02101",
            phone_number="6171234567",
        )

        self.assertEqual(org.address_1, "123 Hospital Ave")
        self.assertEqual(org.address_2, "Suite 100")
        self.assertEqual(org.city, "Boston")
        self.assertEqual(org.state, "MA")
        self.assertEqual(org.country, "US")
        self.assertEqual(org.zip_code, "02101")
        self.assertEqual(org.phone_number, "6171234567")


class ProfileModelTest(TestCase):
    """Test cases for Profile model."""

    databases = ["default", "accounts"]

    def setUp(self):
        self.user = User.objects.db_manager("accounts").create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.organization = baker.make(Organization, name="Test Hospital", _using="accounts")
        self.tier = baker.make(Tier, tier_name="Tier Test", level=2, _using="accounts")

        # Handle profile creation - check if signal created one or create manually
        try:
            self.profile = self.user.profile
            self.profile.organization = self.organization
            self.profile.tier = self.tier
            self.profile.save(using="accounts")
        except Profile.DoesNotExist:
            self.profile = baker.make(
                Profile,
                user=self.user,
                organization=self.organization,
                tier=self.tier,
                _using="accounts",
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


class EmailVerificationTokenModelTest(TestCase):
    """Test cases for EmailVerificationToken model."""

    databases = ["default", "accounts"]

    def setUp(self):
        self.user = User.objects.db_manager("accounts").create_user(
            username="tokentest", email="token@example.com", password="testpass123"
        )

    def test_token_creation(self):
        """Test verification token is created with proper defaults."""
        token = EmailVerificationToken.objects.db_manager("accounts").create(user=self.user)

        self.assertIsNotNone(token.token)
        self.assertEqual(
            len(token.token), 64
        )  # Token length was increased to match PasswordResetToken
        self.assertFalse(token.is_used)
        self.assertIsNotNone(token.expires_at)

        # Check expiration is 24 hours from now
        time_diff = token.expires_at - timezone.now()
        self.assertGreater(time_diff.total_seconds(), 23 * 3600)  # > 23 hours
        self.assertLess(time_diff.total_seconds(), 25 * 3600)  # < 25 hours

    def test_token_uniqueness(self):
        """Test that tokens are unique."""
        token1 = EmailVerificationToken.objects.db_manager("accounts").create(user=self.user)

        # Create another user for second token
        user2 = User.objects.db_manager("accounts").create_user(
            username="tokentest2", email="token2@example.com", password="testpass123"
        )
        token2 = EmailVerificationToken.objects.db_manager("accounts").create(user=user2)

        self.assertNotEqual(token1.token, token2.token)

    def test_is_expired_method(self):
        """Test is_expired method works correctly."""
        token = EmailVerificationToken.objects.db_manager("accounts").create(user=self.user)

        # Fresh token should not be expired
        self.assertFalse(token.is_expired())

        # Set expiration to past
        token.expires_at = timezone.now() - timedelta(hours=1)
        self.assertTrue(token.is_expired())

    def test_is_valid_method(self):
        """Test is_valid method checks both used and expired status."""
        token = EmailVerificationToken.objects.db_manager("accounts").create(user=self.user)

        # Fresh token should be valid
        self.assertTrue(token.is_valid())

        # Used token should not be valid
        token.is_used = True
        self.assertFalse(token.is_valid())

        # Reset and test expired
        token.is_used = False
        token.expires_at = timezone.now() - timedelta(hours=1)
        self.assertFalse(token.is_valid())

    def test_str_representation(self):
        """Test string representation of token."""
        token = EmailVerificationToken.objects.db_manager("accounts").create(user=self.user)

        self.assertEqual(str(token), f"Verification token for {self.user.email}")
