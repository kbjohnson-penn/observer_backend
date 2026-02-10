"""
Infrastructure tests for clinical app (database routing, constraints).
Migrated from clinical/tests.py for better organization.
"""

from unittest.mock import MagicMock

from django.test import TestCase

from model_bakery import baker

from accounts.models import Organization, Tier
from clinical.models import Department, Encounter, EncounterFile


class DatabaseRoutingTest(TestCase):
    """Test cases for database routing."""

    databases = ["default", "accounts", "clinical"]

    def test_clinical_models_routing(self):
        """Test that clinical models are routed to clinical database."""
        from shared.db_router import DatabaseRouter

        router = DatabaseRouter()

        # Test reading from clinical database
        read_db = router.db_for_read(Encounter)
        self.assertEqual(read_db, "clinical")

        # Test writing to clinical database
        write_db = router.db_for_write(Encounter)
        self.assertEqual(write_db, "clinical")

    def test_cross_database_relations(self):
        """Test cross-database relationship validation."""
        from shared.db_router import DatabaseRouter

        router = DatabaseRouter()

        # Create mock objects
        clinical_obj = MagicMock()
        clinical_obj._state.db = "clinical"

        accounts_obj = MagicMock()
        accounts_obj._state.db = "accounts"

        # Should not allow cross-database relationships directly
        result = router.allow_relation(clinical_obj, accounts_obj)
        self.assertFalse(result)

        # Same database relationships should be allowed
        clinical_obj2 = MagicMock()
        clinical_obj2._state.db = "clinical"

        result = router.allow_relation(clinical_obj, clinical_obj2)
        self.assertTrue(result)


class DatabaseConstraintTest(TestCase):
    """Test cases for database constraints."""

    databases = ["default", "accounts", "clinical"]

    def test_organization_name_unique_constraint(self):
        """Test that organization names must be unique."""
        # Create first organization
        _org1 = baker.make(Organization, name="Test Hospital", _using="accounts")

        # Attempting to create another with same name should raise error
        with self.assertRaises(Exception):
            baker.make(Organization, name="Test Hospital", _using="accounts")

    def test_encounter_file_unique_constraint(self):
        """Test that file paths must be unique per encounter."""
        tier = baker.make(Tier, tier_name="Test Tier", level=2, _using="accounts")
        department = baker.make(Department, name="Cardiology", _using="clinical")
        encounter = baker.make(
            Encounter, department=department, tier_level=tier.id, _using="clinical"
        )

        # Create first file
        file1 = baker.make(EncounterFile, encounter=encounter, file_path="test/path/video.mp4")

        # Attempting to create another file with same path for same encounter should fail
        with self.assertRaises(Exception):
            baker.make(EncounterFile, encounter=encounter, file_path="test/path/video.mp4")

    def test_department_unique_constraint(self):
        """Test that department names must be unique."""
        from clinical.models import Department

        # Create first department
        dept1 = baker.make(Department, name="Cardiology", _using="clinical")

        # Attempting to create another with same name should raise error
        with self.assertRaises(Exception):
            baker.make(Department, name="Cardiology", _using="clinical")
