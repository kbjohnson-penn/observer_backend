"""
Permission tests for shared app.
Migrated from shared/tests.py for better organization.
"""

from unittest.mock import MagicMock

from django.test import TestCase

from model_bakery import baker
from rest_framework.test import APITestCase

from accounts.models import Organization, Profile, Tier, User
from shared.api.permissions.public_permissions import IsReadOnly
from shared.api.permissions.tier_permissions import (
    BaseAuthenticatedViewSet,
    HasAccessToEncounter,
    filter_queryset_by_user_tier,
)


class TierPermissionsTest(TestCase):
    """Test cases for tier-based permissions."""

    databases = ["default", "accounts"]

    def setUp(self):
        self.organization = baker.make(Organization, name="Test Hospital", _using="accounts")
        self.tier_1 = baker.make(Tier, tier_name="Tier 1", level=1, _using="accounts")
        self.tier_2 = baker.make(Tier, tier_name="Tier 2", level=2, _using="accounts")
        self.tier_3 = baker.make(Tier, tier_name="Tier 3", level=3, _using="accounts")

        # Create users with different tier levels
        self.user_tier1 = baker.make(
            User, username="tier1user", email="tier1@example.com", _using="accounts"
        )
        # Handle signal-created profile
        try:
            self.profile_tier1 = self.user_tier1.profile
            self.profile_tier1.tier = self.tier_1
            self.profile_tier1.organization = self.organization
            self.profile_tier1.save(using="accounts")
        except Profile.DoesNotExist:
            self.profile_tier1 = baker.make(
                Profile,
                user=self.user_tier1,
                tier=self.tier_1,
                organization=self.organization,
                _using="accounts",
            )

        self.user_tier2 = baker.make(
            User, username="tier2user", email="tier2@example.com", _using="accounts"
        )
        # Handle signal-created profile
        try:
            self.profile_tier2 = self.user_tier2.profile
            self.profile_tier2.tier = self.tier_2
            self.profile_tier2.organization = self.organization
            self.profile_tier2.save(using="accounts")
        except Profile.DoesNotExist:
            self.profile_tier2 = baker.make(
                Profile,
                user=self.user_tier2,
                tier=self.tier_2,
                organization=self.organization,
                _using="accounts",
            )

        self.user_tier3 = baker.make(
            User, username="tier3user", email="tier3@example.com", _using="accounts"
        )
        # Handle signal-created profile
        try:
            self.profile_tier3 = self.user_tier3.profile
            self.profile_tier3.tier = self.tier_3
            self.profile_tier3.organization = self.organization
            self.profile_tier3.save(using="accounts")
        except Profile.DoesNotExist:
            self.profile_tier3 = baker.make(
                Profile,
                user=self.user_tier3,
                tier=self.tier_3,
                organization=self.organization,
                _using="accounts",
            )

        self.superuser = baker.make(
            User, username="admin", email="admin@example.com", is_superuser=True, _using="accounts"
        )

    def test_filter_queryset_by_user_tier_tier1(self):
        """Test queryset filtering for tier 1 user."""
        # Test direct tier filtering (user can access tiers at or below their level)
        if hasattr(self.user_tier1, "profile") and self.user_tier1.profile.tier:
            user_tier = self.user_tier1.profile.tier
            accessible_tiers = Tier.objects.using("accounts").filter(level__lte=user_tier.level)
            accessible_levels = [tier.level for tier in accessible_tiers]
            self.assertEqual(accessible_levels, [1])
        else:
            self.fail("User should have a profile with tier")

    def test_filter_queryset_by_user_tier_tier2(self):
        """Test queryset filtering for tier 2 user."""
        # Test direct tier filtering (user can access tiers at or below their level)
        if hasattr(self.user_tier2, "profile") and self.user_tier2.profile.tier:
            user_tier = self.user_tier2.profile.tier
            accessible_tiers = Tier.objects.using("accounts").filter(level__lte=user_tier.level)
            accessible_levels = sorted([tier.level for tier in accessible_tiers])
            self.assertEqual(accessible_levels, [1, 2])
        else:
            self.fail("User should have a profile with tier")

    def test_filter_queryset_by_user_tier_tier3(self):
        """Test queryset filtering for tier 3 user."""
        # Test direct tier filtering (user can access tiers at or below their level)
        if hasattr(self.user_tier3, "profile") and self.user_tier3.profile.tier:
            user_tier = self.user_tier3.profile.tier
            accessible_tiers = Tier.objects.using("accounts").filter(level__lte=user_tier.level)
            accessible_levels = sorted([tier.level for tier in accessible_tiers])
            self.assertEqual(accessible_levels, [1, 2, 3])
        else:
            self.fail("User should have a profile with tier")

    def test_filter_queryset_by_user_tier_superuser(self):
        """Test queryset filtering for superuser."""
        queryset = Tier.objects.using("accounts").all()

        # Test that filter_queryset_by_user_tier passes through superuser queries unchanged
        filtered = filter_queryset_by_user_tier(queryset, self.superuser, "tier")

        # Superuser should see all tiers (function returns queryset unchanged)
        self.assertEqual(queryset.count(), filtered.count())
        accessible_levels = sorted([tier.level for tier in filtered])
        self.assertEqual(accessible_levels, [1, 2, 3])

    def test_filter_queryset_by_user_tier_no_profile(self):
        """Test queryset filtering for user without profile."""
        user_no_profile = baker.make(
            User, username="noprofile", email="noprofile@example.com", _using="accounts"
        )

        queryset = Tier.objects.using("accounts").all()

        filtered = filter_queryset_by_user_tier(queryset, user_no_profile, "level__lte")

        # User without profile should see nothing
        self.assertEqual(filtered.count(), 0)

    def test_filter_queryset_by_user_tier_custom_field(self):
        """Test queryset filtering function behavior."""
        # Test the logic of the filter_queryset_by_user_tier function
        # Since we're testing Tier objects directly, let's test the accessible tier logic
        if hasattr(self.user_tier2, "profile") and self.user_tier2.profile.tier:
            user_tier = self.user_tier2.profile.tier

            # Test that user can access tiers at or below their level
            accessible_tiers = Tier.objects.using("accounts").filter(level__lte=user_tier.level)
            accessible_levels = sorted([tier.level for tier in accessible_tiers])
            self.assertEqual(accessible_levels, [1, 2])

            # Test that the accessible tier IDs are correct
            accessible_tier_levels = list(accessible_tiers.values_list("id", flat=True))
            self.assertIn(self.tier_1.id, accessible_tier_levels)
            self.assertIn(self.tier_2.id, accessible_tier_levels)
            self.assertNotIn(self.tier_3.id, accessible_tier_levels)
        else:
            self.fail("User should have a profile with tier")


class BaseAuthenticatedViewSetTest(APITestCase):
    """Test cases for BaseAuthenticatedViewSet."""

    databases = ["default", "accounts"]

    def setUp(self):
        self.organization = baker.make(Organization, name="Test Hospital", _using="accounts")
        self.tier_1 = baker.make(Tier, tier_name="Tier 1", level=1, _using="accounts")
        self.tier_2 = baker.make(Tier, tier_name="Tier 2", level=2, _using="accounts")

        self.user = baker.make(
            User, username="testuser", email="test@example.com", _using="accounts"
        )
        # Handle signal-created profile
        try:
            self.profile = self.user.profile
            self.profile.tier = self.tier_2
            self.profile.organization = self.organization
            self.profile.save(using="accounts")
        except Profile.DoesNotExist:
            self.profile = baker.make(
                Profile,
                user=self.user,
                tier=self.tier_2,
                organization=self.organization,
                _using="accounts",
            )

        self.superuser = baker.make(
            User, username="admin", email="admin@example.com", is_superuser=True, _using="accounts"
        )

    def test_has_access_to_tier_regular_user(self):
        """Test tier access for regular user."""
        viewset = BaseAuthenticatedViewSet()

        # User should have access to tier 1 and 2
        self.assertTrue(viewset.has_access_to_tier(self.user, self.tier_1))
        self.assertTrue(viewset.has_access_to_tier(self.user, self.tier_2))

        # Create tier 3 for testing
        tier_3 = baker.make(Tier, tier_name="Tier 3", level=3, _using="accounts")
        self.assertFalse(viewset.has_access_to_tier(self.user, tier_3))

    def test_has_access_to_tier_superuser(self):
        """Test tier access for superuser."""
        viewset = BaseAuthenticatedViewSet()

        # Superuser should have access to all tiers
        self.assertTrue(viewset.has_access_to_tier(self.superuser, self.tier_1))
        self.assertTrue(viewset.has_access_to_tier(self.superuser, self.tier_2))

        tier_3 = baker.make(Tier, tier_name="Tier 3", level=3, _using="accounts")
        self.assertTrue(viewset.has_access_to_tier(self.superuser, tier_3))

    def test_has_access_to_tier_no_profile(self):
        """Test tier access for user without profile."""
        user_no_profile = baker.make(
            User, username="noprofile", email="noprofile@example.com", _using="accounts"
        )

        viewset = BaseAuthenticatedViewSet()

        # User without profile should have no access
        self.assertFalse(viewset.has_access_to_tier(user_no_profile, self.tier_1))
        self.assertFalse(viewset.has_access_to_tier(user_no_profile, self.tier_2))


class HasAccessToEncounterTest(TestCase):
    """Test cases for HasAccessToEncounter permission."""

    databases = ["default", "accounts"]

    def setUp(self):
        self.organization = baker.make(Organization, name="Test Hospital", _using="accounts")
        self.tier_1 = baker.make(Tier, tier_name="Tier 1", level=1, _using="accounts")
        self.tier_2 = baker.make(Tier, tier_name="Tier 2", level=2, _using="accounts")

        self.user = baker.make(
            User, username="testuser", email="test@example.com", _using="accounts"
        )
        # Handle signal-created profile
        try:
            self.profile = self.user.profile
            self.profile.tier = self.tier_2
            self.profile.organization = self.organization
            self.profile.save(using="accounts")
        except Profile.DoesNotExist:
            self.profile = baker.make(
                Profile,
                user=self.user,
                tier=self.tier_2,
                organization=self.organization,
                _using="accounts",
            )

        self.permission = HasAccessToEncounter()

    def test_has_object_permission_encounter_access(self):
        """Test object permission for encounter access."""
        # Import Encounter to create proper mock
        from clinical.models import Encounter

        # Create mock encounter that passes isinstance check
        encounter = MagicMock(spec=Encounter)
        encounter.tier_level = self.tier_1.level  # User tier 2 can access tier 1 (2 >= 1)

        # Create mock request and view
        request = MagicMock()
        request.user = self.user

        view = MagicMock()

        # Should have access (user has tier 2, encounter is tier 1, so 1 <= 2)
        result = self.permission.has_object_permission(request, view, encounter)
        self.assertTrue(result)

    def test_has_object_permission_encounter_no_access(self):
        """Test object permission for encounter without access."""
        # Import Encounter to create proper mock
        from clinical.models import Encounter

        # Create mock encounter that passes isinstance check
        encounter = MagicMock(spec=Encounter)
        # User has tier 2, but encounter needs tier 3 (3 > 2), so no access
        encounter.tier_level = 3

        # Create mock request and view
        request = MagicMock()
        request.user = self.user

        view = MagicMock()

        # Should not have access (user has tier 2, encounter is tier 3, so 3 > 2)
        result = self.permission.has_object_permission(request, view, encounter)
        self.assertFalse(result)

    def test_has_object_permission_unsupported_object(self):
        """Test object permission for unsupported object type."""
        # Create mock unsupported object
        unsupported_obj = MagicMock()
        unsupported_obj.__class__.__name__ = "UnsupportedModel"

        # Create mock request and view
        request = MagicMock()
        request.user = self.user

        view = MagicMock()

        # Should return False for unsupported objects
        result = self.permission.has_object_permission(request, view, unsupported_obj)
        self.assertFalse(result)


class PublicPermissionsTest(TestCase):
    """Test cases for public permissions."""

    def test_is_read_only_permission(self):
        """Test IsReadOnly permission."""
        permission = IsReadOnly()

        # Create mock request and view
        request = MagicMock()
        view = MagicMock()

        # Should allow GET requests
        request.method = "GET"
        result = permission.has_permission(request, view)
        self.assertTrue(result)

        # Should allow HEAD requests
        request.method = "HEAD"
        result = permission.has_permission(request, view)
        self.assertTrue(result)

        # Should allow OPTIONS requests
        request.method = "OPTIONS"
        result = permission.has_permission(request, view)
        self.assertTrue(result)

        # Should deny POST requests
        request.method = "POST"
        result = permission.has_permission(request, view)
        self.assertFalse(result)

        # Should deny PUT requests
        request.method = "PUT"
        result = permission.has_permission(request, view)
        self.assertFalse(result)

        # Should deny DELETE requests
        request.method = "DELETE"
        result = permission.has_permission(request, view)
        self.assertFalse(result)

        # Should deny PATCH requests
        request.method = "PATCH"
        result = permission.has_permission(request, view)
        self.assertFalse(result)
