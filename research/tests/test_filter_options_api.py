"""
Tests for FilterOptions API endpoint.
Tests authentication, response structure, and demographic filter options including NULL handling.
"""

from django.test import override_settings

from model_bakery import baker
from rest_framework import status

from accounts.models import Tier
from research.models import Person, VisitOccurrence

from .test_base import BaseResearchAPITestCase


# Disable caching for all filter options tests to avoid stale responses
@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}})
class FilterOptionsAuthenticationTest(BaseResearchAPITestCase):
    """Test authentication and authorization for FilterOptions endpoint."""

    def test_get_filter_options_authenticated(self):
        """Test retrieving filter options for authenticated user returns 200."""
        self.authenticate_user()

        response = self.client.get("/api/v1/research/private/filter-options/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("demographics", response.data)
        self.assertIn("visit_options", response.data)
        self.assertIn("clinical_options", response.data)
        self.assertIn("total_accessible_visits", response.data)

    def test_get_filter_options_unauthorized(self):
        """Test that unauthenticated requests return 401."""
        response = self.client.get("/api/v1/research/private/filter-options/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}})
class FilterOptionsStructureTest(BaseResearchAPITestCase):
    """Test response structure of FilterOptions endpoint."""

    def test_filter_options_returns_demographics_structure(self):
        """Test that demographics section has expected structure."""
        self.authenticate_user()

        response = self.client.get("/api/v1/research/private/filter-options/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        demographics = response.data["demographics"]
        self.assertIn("genders", demographics)
        self.assertIn("races", demographics)
        self.assertIn("ethnicities", demographics)
        self.assertIn("year_of_birth_range", demographics)
        self.assertIn("min", demographics["year_of_birth_range"])
        self.assertIn("max", demographics["year_of_birth_range"])

    def test_filter_options_returns_visit_options_structure(self):
        """Test that visit_options section has expected structure."""
        self.authenticate_user()

        response = self.client.get("/api/v1/research/private/filter-options/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        visit_options = response.data["visit_options"]
        self.assertIn("tiers", visit_options)
        self.assertIn("visit_sources", visit_options)
        self.assertIn("date_range", visit_options)
        self.assertIn("earliest", visit_options["date_range"])
        self.assertIn("latest", visit_options["date_range"])

    def test_filter_options_returns_clinical_options_structure(self):
        """Test that clinical_options section has expected structure."""
        self.authenticate_user()

        response = self.client.get("/api/v1/research/private/filter-options/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        clinical_options = response.data["clinical_options"]
        self.assertIn("conditions", clinical_options)
        self.assertIn("labs", clinical_options)
        self.assertIn("drugs", clinical_options)
        self.assertIn("procedures", clinical_options)
        self.assertIn("notes", clinical_options)
        self.assertIn("observations", clinical_options)
        self.assertIn("measurements", clinical_options)


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}})
class FilterOptionsGenderTest(BaseResearchAPITestCase):
    """Test gender filter options."""

    def test_filter_options_returns_gender_values(self):
        """Test that actual gender values are returned."""
        self.authenticate_user()

        # Set up person and provider with known genders
        self.person.gender_source_value = "M"
        self.person.save(using="research")
        self.provider.gender_source_value = "F"
        self.provider.save(using="research")

        response = self.client.get("/api/v1/research/private/filter-options/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        genders = response.data["demographics"]["genders"]
        self.assertIn("M", genders)

    def test_filter_options_returns_multiple_gender_values(self):
        """Test that multiple distinct gender values are returned."""
        self.authenticate_user()

        # Set up person and provider with known genders (no NULLs)
        self.person.gender_source_value = "M"
        self.person.save(using="research")
        self.provider.gender_source_value = "M"
        self.provider.save(using="research")

        # Create another person with different gender
        person_female = baker.make(Person, gender_source_value="F", _using="research")
        baker.make(
            VisitOccurrence,
            person=person_female,
            provider=self.provider,
            tier_level=self.tier.level,
            _using="research",
        )

        response = self.client.get("/api/v1/research/private/filter-options/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        genders = response.data["demographics"]["genders"]
        self.assertIn("M", genders)
        self.assertIn("F", genders)

    def test_filter_options_includes_null_marker_for_gender(self):
        """Test that __NULL__ marker is included when NULL gender values exist."""
        self.authenticate_user()

        # Set base provider to have non-null gender
        self.provider.gender_source_value = "F"
        self.provider.save(using="research")

        # Create person with NULL gender (base person already has NULL from baker.make)
        person_null_gender = baker.make(Person, gender_source_value=None, _using="research")
        baker.make(
            VisitOccurrence,
            person=person_null_gender,
            provider=self.provider,
            tier_level=self.tier.level,
            _using="research",
        )

        # Create person with known gender
        person_with_gender = baker.make(Person, gender_source_value="M", _using="research")
        baker.make(
            VisitOccurrence,
            person=person_with_gender,
            provider=self.provider,
            tier_level=self.tier.level,
            _using="research",
        )

        response = self.client.get("/api/v1/research/private/filter-options/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        genders = response.data["demographics"]["genders"]
        self.assertIn("__NULL__", genders)
        self.assertIn("M", genders)

    def test_filter_options_no_null_gender_when_all_populated(self):
        """Test that __NULL__ marker is NOT included when all gender values are populated."""
        self.authenticate_user()

        # Ensure person and provider both have non-null genders
        self.person.gender_source_value = "F"
        self.person.save(using="research")

        self.provider.gender_source_value = "M"
        self.provider.save(using="research")

        response = self.client.get("/api/v1/research/private/filter-options/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        genders = response.data["demographics"]["genders"]
        self.assertNotIn("__NULL__", genders)
        self.assertIn("F", genders)
        self.assertIn("M", genders)


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}})
class FilterOptionsRaceTest(BaseResearchAPITestCase):
    """Test race filter options."""

    def test_filter_options_returns_race_values(self):
        """Test that actual race values are returned."""
        self.authenticate_user()

        # Set up person and provider with known races
        self.person.race_source_value = "W"
        self.person.save(using="research")
        self.provider.race_source_value = "A"
        self.provider.save(using="research")

        response = self.client.get("/api/v1/research/private/filter-options/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        races = response.data["demographics"]["races"]
        self.assertIn("W", races)

    def test_filter_options_includes_null_marker_for_race(self):
        """Test that __NULL__ marker is included when NULL race values exist."""
        self.authenticate_user()

        # Set base provider to have non-null race
        self.provider.race_source_value = "A"
        self.provider.save(using="research")

        # Create person with NULL race (base person already has NULL from baker.make)
        person_null_race = baker.make(Person, race_source_value=None, _using="research")
        baker.make(
            VisitOccurrence,
            person=person_null_race,
            provider=self.provider,
            tier_level=self.tier.level,
            _using="research",
        )

        # Create person with known race
        person_with_race = baker.make(Person, race_source_value="W", _using="research")
        baker.make(
            VisitOccurrence,
            person=person_with_race,
            provider=self.provider,
            tier_level=self.tier.level,
            _using="research",
        )

        response = self.client.get("/api/v1/research/private/filter-options/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        races = response.data["demographics"]["races"]
        self.assertIn("__NULL__", races)
        self.assertIn("W", races)


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}})
class FilterOptionsEthnicityTest(BaseResearchAPITestCase):
    """Test ethnicity filter options."""

    def test_filter_options_returns_ethnicity_values(self):
        """Test that actual ethnicity values are returned."""
        self.authenticate_user()

        # Set up person and provider with known ethnicities
        self.person.ethnicity_source_value = "NH"
        self.person.save(using="research")
        self.provider.ethnicity_source_value = "H"
        self.provider.save(using="research")

        response = self.client.get("/api/v1/research/private/filter-options/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ethnicities = response.data["demographics"]["ethnicities"]
        self.assertIn("NH", ethnicities)

    def test_filter_options_includes_null_marker_for_ethnicity(self):
        """Test that __NULL__ marker is included when NULL ethnicity values exist."""
        self.authenticate_user()

        # Set base provider to have non-null ethnicity
        self.provider.ethnicity_source_value = "H"
        self.provider.save(using="research")

        # Create person with NULL ethnicity (base person already has NULL from baker.make)
        person_null_ethnicity = baker.make(Person, ethnicity_source_value=None, _using="research")
        baker.make(
            VisitOccurrence,
            person=person_null_ethnicity,
            provider=self.provider,
            tier_level=self.tier.level,
            _using="research",
        )

        # Create person with known ethnicity
        person_with_ethnicity = baker.make(Person, ethnicity_source_value="NH", _using="research")
        baker.make(
            VisitOccurrence,
            person=person_with_ethnicity,
            provider=self.provider,
            tier_level=self.tier.level,
            _using="research",
        )

        response = self.client.get("/api/v1/research/private/filter-options/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ethnicities = response.data["demographics"]["ethnicities"]
        self.assertIn("__NULL__", ethnicities)
        self.assertIn("NH", ethnicities)


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}})
class FilterOptionsEdgeCasesTest(BaseResearchAPITestCase):
    """Test edge cases for FilterOptions endpoint."""

    def test_filter_options_null_marker_from_provider(self):
        """Test that __NULL__ marker is included when NULL values exist in Provider."""
        self.authenticate_user()

        # Ensure person has non-null gender but provider has null
        self.person.gender_source_value = "M"
        self.person.save(using="research")

        self.provider.gender_source_value = None
        self.provider.save(using="research")

        response = self.client.get("/api/v1/research/private/filter-options/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        genders = response.data["demographics"]["genders"]
        self.assertIn("__NULL__", genders)
        self.assertIn("M", genders)

    def test_filter_options_excludes_empty_strings(self):
        """Test that empty strings are excluded from filter options."""
        self.authenticate_user()

        # Set base person/provider to have non-null genders
        self.person.gender_source_value = "M"
        self.person.save(using="research")
        self.provider.gender_source_value = "M"
        self.provider.save(using="research")

        # Create person with empty string gender
        person_empty_gender = baker.make(Person, gender_source_value="", _using="research")
        baker.make(
            VisitOccurrence,
            person=person_empty_gender,
            provider=self.provider,
            tier_level=self.tier.level,
            _using="research",
        )

        # Create person with valid gender
        person_with_gender = baker.make(Person, gender_source_value="F", _using="research")
        baker.make(
            VisitOccurrence,
            person=person_with_gender,
            provider=self.provider,
            tier_level=self.tier.level,
            _using="research",
        )

        response = self.client.get("/api/v1/research/private/filter-options/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        genders = response.data["demographics"]["genders"]
        self.assertNotIn("", genders)
        self.assertIn("F", genders)

    def test_filter_options_respects_tier_access(self):
        """Test that filter options only include values from accessible visits."""
        self.authenticate_user()

        # Set base person/provider to have non-null genders
        self.person.gender_source_value = "M"
        self.person.save(using="research")
        self.provider.gender_source_value = "F"
        self.provider.save(using="research")

        # Create a higher tier that user cannot access
        tier_high = baker.make(Tier, tier_name="Tier 5", level=5, _using="accounts")

        # Create person with unique gender on inaccessible tier
        person_inaccessible = baker.make(Person, gender_source_value="X", _using="research")
        baker.make(
            VisitOccurrence,
            person=person_inaccessible,
            provider=self.provider,
            tier_level=tier_high.id,
            _using="research",
        )

        response = self.client.get("/api/v1/research/private/filter-options/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        genders = response.data["demographics"]["genders"]
        # "X" should not appear since it's on inaccessible tier
        self.assertNotIn("X", genders)
        self.assertIn("M", genders)

    def test_filter_options_returns_total_accessible_visits(self):
        """Test that total_accessible_visits count is correct."""
        self.authenticate_user()

        # We have 1 visit from base setup
        response = self.client.get("/api/v1/research/private/filter-options/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_accessible_visits"], 1)

        # Add another accessible visit
        person2 = baker.make(Person, _using="research")
        baker.make(
            VisitOccurrence,
            person=person2,
            provider=self.provider,
            tier_level=self.tier.level,
            _using="research",
        )

        response = self.client.get("/api/v1/research/private/filter-options/")
        self.assertEqual(response.data["total_accessible_visits"], 2)

    def test_filter_options_genders_are_sorted(self):
        """Test that gender values are sorted alphabetically with __NULL__ at end."""
        self.authenticate_user()

        # Set base provider to non-null so we can control when NULL appears
        self.provider.gender_source_value = "X"
        self.provider.save(using="research")

        # Create persons with different genders
        self.person.gender_source_value = "M"
        self.person.save(using="research")

        person_f = baker.make(Person, gender_source_value="F", _using="research")
        baker.make(
            VisitOccurrence,
            person=person_f,
            provider=self.provider,
            tier_level=self.tier.level,
            _using="research",
        )

        person_null = baker.make(Person, gender_source_value=None, _using="research")
        baker.make(
            VisitOccurrence,
            person=person_null,
            provider=self.provider,
            tier_level=self.tier.level,
            _using="research",
        )

        response = self.client.get("/api/v1/research/private/filter-options/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        genders = response.data["demographics"]["genders"]

        # Check __NULL__ is at the end
        self.assertEqual(genders[-1], "__NULL__")
        # Check non-null values are sorted
        non_null_genders = [g for g in genders if g != "__NULL__"]
        self.assertEqual(non_null_genders, sorted(non_null_genders))
