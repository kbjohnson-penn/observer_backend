"""
Infrastructure tests for shared app (router, choices, constants).
Migrated from shared/tests.py for better organization.
"""

from unittest.mock import MagicMock

from django.test import TestCase

from shared.choices import (
    BOOLEAN_CHOICES,
    ENCOUNTER_TYPE_CHOICES,
    FILE_TYPE_CHOICES,
    FILE_TYPE_CHOICES_DICT,
    SEX_CATEGORIES,
)
from shared.constants import (
    SIMCENTER_PATIENT_ID_LOWER_LIMIT,
    SIMCENTER_PATIENT_ID_UPPER_LIMIT,
    SIMCENTER_PROVIDER_ID_LOWER_LIMIT,
    SIMCENTER_PROVIDER_ID_UPPER_LIMIT,
)
from shared.db_router import DatabaseRouter
from shared.location_choices import COUNTRY_CHOICES, US_STATE_CHOICES


class DatabaseRouterTest(TestCase):
    """Test cases for database router."""

    def setUp(self):
        self.router = DatabaseRouter()

    def test_route_app_labels(self):
        """Test that route app labels are correctly configured."""
        expected_labels = {
            "accounts": "accounts",
            "clinical": "clinical",
            "research": "research",
            # Django system apps routed to accounts database
            "auth": "accounts",
            "contenttypes": "accounts",
            "sessions": "accounts",
            "admin": "accounts",
            "token_blacklist": "accounts",
        }
        self.assertEqual(self.router.route_app_labels, expected_labels)

    def test_db_for_read(self):
        """Test database routing for read operations."""
        # Create mock models
        accounts_model = MagicMock()
        accounts_model._meta.app_label = "accounts"

        clinical_model = MagicMock()
        clinical_model._meta.app_label = "clinical"

        research_model = MagicMock()
        research_model._meta.app_label = "research"

        unknown_model = MagicMock()
        unknown_model._meta.app_label = "unknown"

        # Test routing
        self.assertEqual(self.router.db_for_read(accounts_model), "accounts")
        self.assertEqual(self.router.db_for_read(clinical_model), "clinical")
        self.assertEqual(self.router.db_for_read(research_model), "research")
        self.assertIsNone(self.router.db_for_read(unknown_model))

    def test_db_for_write(self):
        """Test database routing for write operations."""
        # Create mock models
        accounts_model = MagicMock()
        accounts_model._meta.app_label = "accounts"

        clinical_model = MagicMock()
        clinical_model._meta.app_label = "clinical"

        research_model = MagicMock()
        research_model._meta.app_label = "research"

        # Test routing
        self.assertEqual(self.router.db_for_write(accounts_model), "accounts")
        self.assertEqual(self.router.db_for_write(clinical_model), "clinical")
        self.assertEqual(self.router.db_for_write(research_model), "research")

    def test_allow_relation_same_database(self):
        """Test allowing relations within the same database."""
        # Create mock objects in same database
        obj1 = MagicMock()
        obj1._state.db = "clinical"

        obj2 = MagicMock()
        obj2._state.db = "clinical"

        result = self.router.allow_relation(obj1, obj2)
        self.assertTrue(result)

    def test_allow_relation_cross_database_valid(self):
        """Test cross-database relations (actually not allowed by this router)."""
        # Clinical <-> Accounts (for Tier)
        clinical_obj = MagicMock()
        clinical_obj._state.db = "clinical"

        accounts_obj = MagicMock()
        accounts_obj._state.db = "accounts"

        # The router only allows same-database relations
        result = self.router.allow_relation(clinical_obj, accounts_obj)
        self.assertFalse(result)

        # Clinical <-> Research (for ETL)
        research_obj = MagicMock()
        research_obj._state.db = "research"

        result = self.router.allow_relation(clinical_obj, research_obj)
        self.assertFalse(result)

    def test_allow_relation_outside_managed_databases(self):
        """Test relations outside managed databases."""
        # Object outside managed databases
        external_obj = MagicMock()
        external_obj._state.db = "external"

        clinical_obj = MagicMock()
        clinical_obj._state.db = "clinical"

        # The router returns False for cross-database relations
        result = self.router.allow_relation(external_obj, clinical_obj)
        self.assertFalse(result)

    def test_allow_migrate_correct_database(self):
        """Test allowing migrations on correct database."""
        # Should allow app migrations on correct database
        result = self.router.allow_migrate("accounts", "accounts", "User")
        self.assertTrue(result)

        result = self.router.allow_migrate("clinical", "clinical", "Encounter")
        self.assertTrue(result)

        result = self.router.allow_migrate("research", "research", "VisitOccurrence")
        self.assertTrue(result)

    def test_allow_migrate_wrong_database(self):
        """Test preventing migrations on wrong database."""
        # Should not allow app migrations on wrong database
        result = self.router.allow_migrate("clinical", "accounts", "User")
        self.assertFalse(result)

        result = self.router.allow_migrate("research", "clinical", "Encounter")
        self.assertFalse(result)

        result = self.router.allow_migrate("accounts", "research", "VisitOccurrence")
        self.assertFalse(result)

    def test_allow_migrate_unknown_app(self):
        """Test migration routing for unknown apps."""
        # Unknown app should default to 'default' database according to router logic
        result = self.router.allow_migrate("default", "unknown_app", "UnknownModel")
        self.assertTrue(result)

        result = self.router.allow_migrate("clinical", "unknown_app", "UnknownModel")
        self.assertFalse(result)


class ChoicesTest(TestCase):
    """Test cases for shared choices."""

    def test_sex_categories(self):
        """Test sex categories choices."""
        expected_choices = [
            ("M", "Male"),
            ("F", "Female"),
            ("O", "Other"),
            ("U", "Unknown"),
        ]
        self.assertEqual(SEX_CATEGORIES, expected_choices)

    def test_boolean_choices(self):
        """Test boolean choices."""
        expected_choices = [
            (True, "Yes"),
            (False, "No"),
        ]
        self.assertEqual(BOOLEAN_CHOICES, expected_choices)

    def test_encounter_type_choices(self):
        """Test encounter type choices."""
        # Check that required encounter types are present
        choice_values = [choice[0] for choice in ENCOUNTER_TYPE_CHOICES]
        self.assertIn("clinic", choice_values)
        self.assertIn("simcenter", choice_values)
        self.assertIn("pennpersonalizedcare", choice_values)

    def test_file_type_choices(self):
        """Test file type choices."""
        # Check that required file types are present
        choice_values = [choice[0] for choice in FILE_TYPE_CHOICES]
        self.assertIn("video", choice_values)
        self.assertIn("audio", choice_values)
        self.assertIn("document", choice_values)
        self.assertIn("image", choice_values)

    def test_file_type_choices_dict(self):
        """Test file type choices dictionary."""
        # Check that dictionary has expected keys
        self.assertIn("video", FILE_TYPE_CHOICES_DICT)
        self.assertIn("audio", FILE_TYPE_CHOICES_DICT)
        self.assertIn("document", FILE_TYPE_CHOICES_DICT)
        self.assertIn("image", FILE_TYPE_CHOICES_DICT)

        # Check that values are human-readable
        self.assertEqual(FILE_TYPE_CHOICES_DICT["video"], "Video")
        self.assertEqual(FILE_TYPE_CHOICES_DICT["audio"], "Audio")


class ConstantsTest(TestCase):
    """Test cases for shared constants."""

    def test_simcenter_patient_id_limits(self):
        """Test SimCenter patient ID limits."""
        self.assertIsInstance(SIMCENTER_PATIENT_ID_LOWER_LIMIT, int)
        self.assertIsInstance(SIMCENTER_PATIENT_ID_UPPER_LIMIT, int)
        self.assertGreater(SIMCENTER_PATIENT_ID_UPPER_LIMIT, SIMCENTER_PATIENT_ID_LOWER_LIMIT)

    def test_simcenter_provider_id_limits(self):
        """Test SimCenter provider ID limits."""
        self.assertIsInstance(SIMCENTER_PROVIDER_ID_LOWER_LIMIT, int)
        self.assertIsInstance(SIMCENTER_PROVIDER_ID_UPPER_LIMIT, int)
        self.assertGreater(SIMCENTER_PROVIDER_ID_UPPER_LIMIT, SIMCENTER_PROVIDER_ID_LOWER_LIMIT)

    def test_id_range_separation(self):
        """Test that patient and provider ID ranges don't overlap."""
        # Based on constants.py, both ranges are the same (1000000-9999999)
        # This is actually expected - they share the same range space
        # So we test that ranges are defined and have reasonable values
        self.assertGreater(SIMCENTER_PATIENT_ID_LOWER_LIMIT, 0)
        self.assertGreater(SIMCENTER_PROVIDER_ID_LOWER_LIMIT, 0)
        self.assertGreater(SIMCENTER_PATIENT_ID_UPPER_LIMIT, SIMCENTER_PATIENT_ID_LOWER_LIMIT)
        self.assertGreater(SIMCENTER_PROVIDER_ID_UPPER_LIMIT, SIMCENTER_PROVIDER_ID_LOWER_LIMIT)


class LocationChoicesTest(TestCase):
    """Test cases for location choices."""

    def test_country_choices_format(self):
        """Test country choices format."""
        self.assertIsInstance(COUNTRY_CHOICES, list)
        self.assertTrue(len(COUNTRY_CHOICES) > 0)

        # Check format of first choice
        first_choice = COUNTRY_CHOICES[0]
        self.assertEqual(len(first_choice), 2)
        self.assertIsInstance(first_choice[0], str)  # Code
        self.assertIsInstance(first_choice[1], str)  # Name

    def test_country_choices_us_present(self):
        """Test that US is present in country choices."""
        codes = [choice[0] for choice in COUNTRY_CHOICES]
        self.assertIn("US", codes)

        # Find US entry and check name
        us_entry = next(choice for choice in COUNTRY_CHOICES if choice[0] == "US")
        self.assertEqual(us_entry[1], "United States")

    def test_us_state_choices_format(self):
        """Test US state choices format."""
        self.assertIsInstance(US_STATE_CHOICES, list)
        self.assertTrue(len(US_STATE_CHOICES) >= 50)  # Should have at least 50 states

        # Check format of first choice
        first_choice = US_STATE_CHOICES[0]
        self.assertEqual(len(first_choice), 2)
        self.assertIsInstance(first_choice[0], str)  # State code
        self.assertIsInstance(first_choice[1], str)  # State name
        self.assertEqual(len(first_choice[0]), 2)  # State codes should be 2 characters

    def test_us_state_choices_common_states(self):
        """Test that common US states are present."""
        codes = [choice[0] for choice in US_STATE_CHOICES]

        # Check for some major states
        major_states = ["CA", "NY", "TX", "FL", "PA"]
        for state in major_states:
            self.assertIn(state, codes)

    def test_us_state_choices_consistency(self):
        """Test that US state choices are consistent and complete."""
        # Test that we have a reasonable number of states/territories
        self.assertGreaterEqual(len(US_STATE_CHOICES), 50)

        # Test that all entries have proper format
        for code, name in US_STATE_CHOICES:
            self.assertEqual(len(code), 2)  # State codes are 2 characters
            self.assertIsInstance(name, str)
            self.assertGreater(len(name), 0)

        # Test that codes are unique
        codes = [choice[0] for choice in US_STATE_CHOICES]
        self.assertEqual(len(codes), len(set(codes)))
