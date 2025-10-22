"""
Tests for edge cases and administrative access.
Empty results, superuser access, and boundary conditions.
"""

from django.contrib.auth import get_user_model

from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Organization, Profile, Tier
from research.models import Person, Provider, VisitOccurrence

User = get_user_model()


class EmptyResultsTest(APITestCase):
    """Test cases for users with no accessible data."""

    databases = ["accounts", "research", "clinical"]

    def setUp(self):
        """Set up user with no accessible data."""
        self.client = APIClient()

        self.organization = baker.make(Organization, name="Research Institute", _using="accounts")
        self.tier1 = baker.make(Tier, tier_name="Tier 1", level=1, _using="accounts")
        self.tier2 = baker.make(Tier, tier_name="Tier 2", level=2, _using="accounts")

        # Create user with tier 1 access
        self.user = baker.make(User, username="testuser", _using="accounts")
        self.user.save(using="accounts")
        if hasattr(self.user, "profile") and self.user.profile:
            self.profile = self.user.profile
            self.profile.tier = self.tier1
            self.profile.organization = self.organization
            self.profile.save(using="accounts")
        else:
            self.profile = baker.make(
                Profile,
                user=self.user,
                tier=self.tier1,
                organization=self.organization,
                _using="accounts",
            )

        # Create data only accessible to tier 2 users
        self.person = baker.make(Person, _using="research")
        self.provider = baker.make(Provider, _using="research")
        self.visit = baker.make(
            VisitOccurrence,
            person=self.person,
            provider=self.provider,
            tier_id=self.tier2.id,
            _using="research",
        )

    def authenticate_user(self):
        """Authenticate user."""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        return refresh.access_token

    def test_empty_visits_list(self):
        """Test empty results when user has no accessible visits."""
        self.authenticate_user()

        response = self.client.get("/api/v1/research/private/visits/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_empty_persons_list(self):
        """Test empty results when user has no accessible persons."""
        self.authenticate_user()

        response = self.client.get("/api/v1/research/private/persons/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_empty_providers_list(self):
        """Test empty results when user has no accessible providers."""
        self.authenticate_user()

        response = self.client.get("/api/v1/research/private/providers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)


class SuperuserAccessTest(APITestCase):
    """Test cases for superuser access."""

    databases = ["accounts", "research", "clinical"]

    def setUp(self):
        """Set up superuser test scenario."""
        self.client = APIClient()

        self.organization = baker.make(Organization, name="Research Institute", _using="accounts")
        self.tier1 = baker.make(Tier, tier_name="Tier 1", level=1, _using="accounts")
        self.tier3 = baker.make(Tier, tier_name="Tier 3", level=3, _using="accounts")

        # Create superuser
        self.superuser = baker.make(User, username="admin", is_superuser=True, _using="accounts")
        self.superuser.save(using="accounts")
        # Superuser might not have a profile, but should still have access

        # Create data across different tiers
        self.person1 = baker.make(Person, _using="research")
        self.person3 = baker.make(Person, _using="research")
        self.provider1 = baker.make(Provider, _using="research")
        self.provider3 = baker.make(Provider, _using="research")

        self.visit1 = baker.make(
            VisitOccurrence,
            person=self.person1,
            provider=self.provider1,
            tier_id=self.tier1.id,
            _using="research",
        )
        self.visit3 = baker.make(
            VisitOccurrence,
            person=self.person3,
            provider=self.provider3,
            tier_id=self.tier3.id,
            _using="research",
        )

    def authenticate_superuser(self):
        """Authenticate superuser."""
        refresh = RefreshToken.for_user(self.superuser)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        return refresh.access_token

    def test_superuser_sees_all_visits(self):
        """Test superuser can access all visits regardless of tier."""
        self.authenticate_superuser()

        response = self.client.get("/api/v1/research/private/visits/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_superuser_sees_all_persons(self):
        """Test superuser can access all persons regardless of tier."""
        self.authenticate_superuser()

        response = self.client.get("/api/v1/research/private/persons/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_superuser_sees_all_providers(self):
        """Test superuser can access all providers regardless of tier."""
        self.authenticate_superuser()

        response = self.client.get("/api/v1/research/private/providers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
