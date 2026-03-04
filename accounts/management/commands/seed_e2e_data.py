"""
Management command to seed deterministic test data for E2E tests.

Usage:
    python manage.py seed_e2e_data
    python manage.py seed_e2e_data --teardown   # Remove all e2e_ prefixed data

Credentials created (all passwords: E2eTestPass123!):
    - e2e_admin       (Tier 5, verified, active)
    - e2e_tier1       (Tier 1, verified, active)
    - e2e_unverified  (inactive, email not verified)
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.models.organization_models import Organization
from accounts.models.profile_models import Profile
from accounts.models.tier_models import Tier

User = get_user_model()

E2E_PASSWORD = "E2eTestPass123!"

E2E_USERS = [
    {
        "username": "e2e_admin",
        "email": "e2e_admin@example.com",
        "first_name": "E2E",
        "last_name": "Admin",
        "tier_level": 5,
        "is_active": True,
        "email_verified": True,
    },
    {
        "username": "e2e_tier1",
        "email": "e2e_tier1@example.com",
        "first_name": "E2E",
        "last_name": "Tier1",
        "tier_level": 1,
        "is_active": True,
        "email_verified": True,
    },
    {
        "username": "e2e_unverified",
        "email": "e2e_unverified@example.com",
        "first_name": "E2E",
        "last_name": "Unverified",
        "tier_level": None,
        "is_active": False,
        "email_verified": False,
    },
]

TIER_DEFINITIONS = [
    {"tier_name": "Tier 1", "level": 1},
    {"tier_name": "Tier 2", "level": 2},
    {"tier_name": "Tier 3", "level": 3},
    {"tier_name": "Tier 4", "level": 4},
    {"tier_name": "Tier 5", "level": 5},
]


class Command(BaseCommand):
    help = "Seed deterministic E2E test data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--teardown",
            action="store_true",
            help="Remove all e2e_ prefixed test data",
        )

    def handle(self, *args, **options):
        if options["teardown"]:
            self._teardown()
        else:
            self._seed()

    def _seed(self):
        # Create organization
        org, _ = Organization.objects.using("accounts").get_or_create(name="E2E Test Org")

        # Create tiers
        tiers = {}
        for tier_def in TIER_DEFINITIONS:
            tier, _ = Tier.objects.using("accounts").get_or_create(
                level=tier_def["level"],
                defaults={"tier_name": tier_def["tier_name"]},
            )
            tiers[tier_def["level"]] = tier

        # Create users
        for spec in E2E_USERS:
            user, created = User.objects.db_manager("accounts").get_or_create(
                username=spec["username"],
                defaults={
                    "email": spec["email"],
                    "first_name": spec["first_name"],
                    "last_name": spec["last_name"],
                    "is_active": spec["is_active"],
                    "email_verified": spec["email_verified"],
                },
            )
            if created:
                user.set_password(E2E_PASSWORD)
                user.save(using="accounts")
                self.stdout.write(f"  Created user: {spec['username']}")
            else:
                self.stdout.write(f"  User already exists: {spec['username']}")

            # Ensure profile exists with correct tier
            tier = tiers.get(spec["tier_level"]) if spec["tier_level"] else None
            Profile.objects.using("accounts").update_or_create(
                user=user,
                defaults={"organization": org, "tier": tier},
            )

        self.stdout.write(
            self.style.SUCCESS(f"E2E data seeded successfully. Password: {E2E_PASSWORD}")
        )

    def _teardown(self):
        deleted, details = (
            User.objects.using("accounts").filter(username__startswith="e2e_").delete()
        )
        self.stdout.write(self.style.SUCCESS(f"Removed {deleted} E2E-related records"))
