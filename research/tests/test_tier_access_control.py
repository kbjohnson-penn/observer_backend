"""
Tests for tier-based access control across all ViewSets.
Multi-tier scenarios and security validation.
"""

from django.contrib.auth import get_user_model

from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Organization, Profile, Tier
from research.models import Person, Provider, VisitOccurrence

User = get_user_model()


class TierBasedAccessControlTest(APITestCase):
    """Test cases for tier-based access control across all ViewSets."""

    databases = ["accounts", "research", "clinical"]

    def setUp(self):
        """Set up multi-tier test scenario."""
        self.client = APIClient()

        # Create organization
        self.organization = baker.make(Organization, name="Research Institute", _using="accounts")

        # Create multiple tiers
        self.tier1 = baker.make(Tier, tier_name="Tier 1", level=1, _using="accounts")
        self.tier2 = baker.make(Tier, tier_name="Tier 2", level=2, _using="accounts")
        self.tier3 = baker.make(Tier, tier_name="Tier 3", level=3, _using="accounts")

        # Create users with different tier levels
        self.tier1_user = baker.make(User, username="tier1user", _using="accounts")
        self.tier1_user.save(using="accounts")
        if hasattr(self.tier1_user, "profile") and self.tier1_user.profile:
            self.tier1_profile = self.tier1_user.profile
            self.tier1_profile.tier = self.tier1
            self.tier1_profile.organization = self.organization
            self.tier1_profile.save(using="accounts")
        else:
            self.tier1_profile = baker.make(
                Profile,
                user=self.tier1_user,
                tier=self.tier1,
                organization=self.organization,
                _using="accounts",
            )

        self.tier2_user = baker.make(User, username="tier2user", _using="accounts")
        self.tier2_user.save(using="accounts")
        if hasattr(self.tier2_user, "profile") and self.tier2_user.profile:
            self.tier2_profile = self.tier2_user.profile
            self.tier2_profile.tier = self.tier2
            self.tier2_profile.organization = self.organization
            self.tier2_profile.save(using="accounts")
        else:
            self.tier2_profile = baker.make(
                Profile,
                user=self.tier2_user,
                tier=self.tier2,
                organization=self.organization,
                _using="accounts",
            )

        self.tier3_user = baker.make(User, username="tier3user", _using="accounts")
        self.tier3_user.save(using="accounts")
        if hasattr(self.tier3_user, "profile") and self.tier3_user.profile:
            self.tier3_profile = self.tier3_user.profile
            self.tier3_profile.tier = self.tier3
            self.tier3_profile.organization = self.organization
            self.tier3_profile.save(using="accounts")
        else:
            self.tier3_profile = baker.make(
                Profile,
                user=self.tier3_user,
                tier=self.tier3,
                organization=self.organization,
                _using="accounts",
            )

        # Create research data for different tiers
        self.person1 = baker.make(Person, _using="research")
        self.person2 = baker.make(Person, _using="research")
        self.person3 = baker.make(Person, _using="research")

        self.provider1 = baker.make(Provider, _using="research")
        self.provider2 = baker.make(Provider, _using="research")
        self.provider3 = baker.make(Provider, _using="research")

        # Create visits for different tier levels
        self.visit1 = baker.make(
            VisitOccurrence,
            person=self.person1,
            provider=self.provider1,
            tier_level=self.tier1.id,
            _using="research",
        )
        self.visit2 = baker.make(
            VisitOccurrence,
            person=self.person2,
            provider=self.provider2,
            tier_level=self.tier2.id,
            _using="research",
        )
        self.visit3 = baker.make(
            VisitOccurrence,
            person=self.person3,
            provider=self.provider3,
            tier_level=self.tier3.id,
            _using="research",
        )

    def authenticate_user(self, user):
        """Authenticate a specific user."""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        return refresh.access_token

    def test_tier1_user_access(self):
        """Test Tier 1 user can only access Tier 1 data."""
        self.authenticate_user(self.tier1_user)

        # Should see only tier 1 visits
        response = self.client.get("/api/v1/research/private/visits/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.visit1.id)

        # Should see only tier 1 persons
        response = self.client.get("/api/v1/research/private/persons/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.person1.id)

        # Should see only tier 1 providers
        response = self.client.get("/api/v1/research/private/providers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.provider1.id)

    def test_tier2_user_access(self):
        """Test Tier 2 user can access Tier 1 and Tier 2 data."""
        self.authenticate_user(self.tier2_user)

        # Should see tier 1 and tier 2 visits
        response = self.client.get("/api/v1/research/private/visits/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        visit_ids = {visit["id"] for visit in response.data["results"]}
        self.assertEqual(visit_ids, {self.visit1.id, self.visit2.id})

        # Should see tier 1 and tier 2 persons
        response = self.client.get("/api/v1/research/private/persons/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        person_ids = {person["id"] for person in response.data["results"]}
        self.assertEqual(person_ids, {self.person1.id, self.person2.id})

        # Should see tier 1 and tier 2 providers
        response = self.client.get("/api/v1/research/private/providers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        provider_ids = {provider["id"] for provider in response.data["results"]}
        self.assertEqual(provider_ids, {self.provider1.id, self.provider2.id})

    def test_tier3_user_access(self):
        """Test Tier 3 user can access all tier data."""
        self.authenticate_user(self.tier3_user)

        # Should see all visits
        response = self.client.get("/api/v1/research/private/visits/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)

        # Should see all persons
        response = self.client.get("/api/v1/research/private/persons/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)

        # Should see all providers
        response = self.client.get("/api/v1/research/private/providers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)

    def test_tier1_user_cannot_access_higher_tier_detail(self):
        """Test Tier 1 user gets 404 when accessing higher tier data directly."""
        self.authenticate_user(self.tier1_user)

        # Should get 404 for tier 2 visit
        response = self.client.get(f"/api/v1/research/private/visits/{self.visit2.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Should get 404 for tier 3 person
        response = self.client.get(f"/api/v1/research/private/persons/{self.person3.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Should get 404 for tier 2 provider
        response = self.client.get(f"/api/v1/research/private/providers/{self.provider2.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_tier2_user_can_access_lower_tier_detail(self):
        """Test Tier 2 user can access Tier 1 data via detail endpoints."""
        self.authenticate_user(self.tier2_user)

        # Should access tier 1 visit
        response = self.client.get(f"/api/v1/research/private/visits/{self.visit1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.visit1.id)

        # Should access tier 1 person
        response = self.client.get(f"/api/v1/research/private/persons/{self.person1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.person1.id)

        # Should access tier 1 provider
        response = self.client.get(f"/api/v1/research/private/providers/{self.provider1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.provider1.id)
