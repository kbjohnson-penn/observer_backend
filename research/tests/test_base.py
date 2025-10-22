"""
Base test utilities for research API tests.
Shared setup and authentication helpers.
"""

from django.contrib.auth import get_user_model

from model_bakery import baker
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Organization, Profile, Tier
from research.models import Person, Provider, VisitOccurrence

User = get_user_model()


class BaseResearchAPITestCase(APITestCase):
    """Base test case for research API tests with common setup."""

    databases = ["accounts", "research", "clinical"]

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create minimal test data
        self.organization = baker.make(Organization, name="Research Institute", _using="accounts")
        self.tier = baker.make(Tier, tier_name="Tier 1", level=1, _using="accounts")

        self.user = baker.make(User, username="testuser", _using="accounts")
        self.user.save(using="accounts")

        # Get or create the profile (User model might auto-create it)
        if hasattr(self.user, "profile") and self.user.profile:
            self.profile = self.user.profile
            self.profile.tier = self.tier
            self.profile.organization = self.organization
            self.profile.save(using="accounts")
        else:
            self.profile = baker.make(
                Profile,
                user=self.user,
                tier=self.tier,
                organization=self.organization,
                _using="accounts",
            )

        # Create research data
        self.person = baker.make(Person, _using="research")
        self.provider = baker.make(Provider, _using="research")

        self.visit = baker.make(
            VisitOccurrence,
            person=self.person,
            provider=self.provider,
            tier_id=self.tier.id,  # Store tier ID directly
            _using="research",
        )

    def authenticate_user(self):
        """Authenticate user."""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        return refresh.access_token
