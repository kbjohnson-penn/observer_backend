"""
Tests for VisitSearch API endpoint.
Tests authentication, filtering, sorting, and pagination including NULL demographic handling.
"""

from datetime import date

from model_bakery import baker
from rest_framework import status

from accounts.models import Tier
from research.models import Person, Provider, VisitOccurrence

from .test_base import BaseResearchAPITestCase


class VisitSearchAuthenticationTest(BaseResearchAPITestCase):
    """Test authentication and authorization for VisitSearch endpoint."""

    def test_visit_search_authenticated(self):
        """Test that authenticated POST request returns 200 with results."""
        self.authenticate_user()

        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={"filters": {}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)

    def test_visit_search_unauthorized(self):
        """Test that unauthenticated requests return 401."""
        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={"filters": {}},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class VisitSearchBasicFilteringTest(BaseResearchAPITestCase):
    """Test basic filtering capabilities."""

    def test_visit_search_no_filters(self):
        """Test that search with no filters returns all accessible visits."""
        self.authenticate_user()

        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={"filters": {}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_visit_search_filter_by_tier(self):
        """Test filtering by tier_id."""
        self.authenticate_user()

        # Create visit on different tier
        tier2 = baker.make(Tier, tier_name="Tier 2", level=2, _using="accounts")
        person2 = baker.make(Person, _using="research")
        baker.make(
            VisitOccurrence,
            person=person2,
            provider=self.provider,
            tier_id=tier2.id,
            _using="research",
        )

        # Filter for tier 1 only
        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={"filters": {"visit": {"tier_id": [self.tier.id]}}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_visit_search_filter_by_date_range(self):
        """Test filtering by date range."""
        self.authenticate_user()

        # Set specific date on our visit
        self.visit.visit_start_date = date(2024, 6, 15)
        self.visit.save(using="research")

        # Create visit with different date
        person2 = baker.make(Person, _using="research")
        baker.make(
            VisitOccurrence,
            person=person2,
            provider=self.provider,
            tier_id=self.tier.id,
            visit_start_date=date(2024, 1, 15),
            _using="research",
        )

        # Filter for June onwards
        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={"filters": {"visit": {"date_from": "2024-06-01"}}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_visit_search_filter_by_visit_source(self):
        """Test filtering by visit source value."""
        self.authenticate_user()

        # Set specific visit source
        self.visit.visit_source_value = "clinic"
        self.visit.save(using="research")

        # Create visit with different source
        person2 = baker.make(Person, _using="research")
        baker.make(
            VisitOccurrence,
            person=person2,
            provider=self.provider,
            tier_id=self.tier.id,
            visit_source_value="sim_center",
            _using="research",
        )

        # Filter for clinic only
        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={"filters": {"visit": {"visit_source_value": ["clinic"]}}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)


class VisitSearchPersonDemographicFilteringTest(BaseResearchAPITestCase):
    """Test person demographic filtering."""

    def test_visit_search_filter_by_gender(self):
        """Test filtering by single gender value."""
        self.authenticate_user()

        # Set up person with known gender
        self.person.gender_source_value = "M"
        self.person.save(using="research")

        # Create person with different gender
        person_f = baker.make(Person, gender_source_value="F", _using="research")
        baker.make(
            VisitOccurrence,
            person=person_f,
            provider=self.provider,
            tier_id=self.tier.id,
            _using="research",
        )

        # Filter for Male only
        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={"filters": {"person_demographics": {"gender": ["M"]}}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_visit_search_filter_by_multiple_genders(self):
        """Test filtering by multiple gender values."""
        self.authenticate_user()

        # Set up person with known gender
        self.person.gender_source_value = "M"
        self.person.save(using="research")

        # Create person with different gender
        person_f = baker.make(Person, gender_source_value="F", _using="research")
        baker.make(
            VisitOccurrence,
            person=person_f,
            provider=self.provider,
            tier_id=self.tier.id,
            _using="research",
        )

        # Filter for both Male and Female
        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={"filters": {"person_demographics": {"gender": ["M", "F"]}}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_visit_search_filter_by_null_gender(self):
        """Test filtering with __NULL__ returns visits with NULL gender."""
        self.authenticate_user()

        # Set up person with NULL gender
        self.person.gender_source_value = None
        self.person.save(using="research")

        # Create person with known gender
        person_m = baker.make(Person, gender_source_value="M", _using="research")
        baker.make(
            VisitOccurrence,
            person=person_m,
            provider=self.provider,
            tier_id=self.tier.id,
            _using="research",
        )

        # Filter for NULL only
        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={"filters": {"person_demographics": {"gender": ["__NULL__"]}}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        # Verify returned visit has NULL gender person
        self.assertEqual(response.data["results"][0]["patient_id"], self.person.id)

    def test_visit_search_filter_by_gender_and_null(self):
        """Test filtering with both regular value and __NULL__ returns both."""
        self.authenticate_user()

        # Set up person with NULL gender
        self.person.gender_source_value = None
        self.person.save(using="research")

        # Create person with known gender
        person_m = baker.make(Person, gender_source_value="M", _using="research")
        baker.make(
            VisitOccurrence,
            person=person_m,
            provider=self.provider,
            tier_id=self.tier.id,
            _using="research",
        )

        # Create person with different gender (should be excluded)
        person_f = baker.make(Person, gender_source_value="F", _using="research")
        baker.make(
            VisitOccurrence,
            person=person_f,
            provider=self.provider,
            tier_id=self.tier.id,
            _using="research",
        )

        # Filter for Male and NULL
        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={"filters": {"person_demographics": {"gender": ["M", "__NULL__"]}}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_visit_search_filter_by_race(self):
        """Test filtering by race value."""
        self.authenticate_user()

        # Set up person with known race
        self.person.race_source_value = "W"
        self.person.save(using="research")

        # Create person with different race
        person_other = baker.make(Person, race_source_value="A", _using="research")
        baker.make(
            VisitOccurrence,
            person=person_other,
            provider=self.provider,
            tier_id=self.tier.id,
            _using="research",
        )

        # Filter for White only
        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={"filters": {"person_demographics": {"race": ["W"]}}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_visit_search_filter_by_null_race(self):
        """Test filtering with __NULL__ returns visits with NULL race."""
        self.authenticate_user()

        # Set up person with NULL race
        self.person.race_source_value = None
        self.person.save(using="research")

        # Create person with known race
        person_w = baker.make(Person, race_source_value="W", _using="research")
        baker.make(
            VisitOccurrence,
            person=person_w,
            provider=self.provider,
            tier_id=self.tier.id,
            _using="research",
        )

        # Filter for NULL only
        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={"filters": {"person_demographics": {"race": ["__NULL__"]}}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_visit_search_filter_by_ethnicity(self):
        """Test filtering by ethnicity value."""
        self.authenticate_user()

        # Set up person with known ethnicity
        self.person.ethnicity_source_value = "NH"
        self.person.save(using="research")

        # Create person with different ethnicity
        person_other = baker.make(Person, ethnicity_source_value="H", _using="research")
        baker.make(
            VisitOccurrence,
            person=person_other,
            provider=self.provider,
            tier_id=self.tier.id,
            _using="research",
        )

        # Filter for Not Hispanic only
        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={"filters": {"person_demographics": {"ethnicity": ["NH"]}}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_visit_search_filter_by_null_ethnicity(self):
        """Test filtering with __NULL__ returns visits with NULL ethnicity."""
        self.authenticate_user()

        # Set up person with NULL ethnicity
        self.person.ethnicity_source_value = None
        self.person.save(using="research")

        # Create person with known ethnicity
        person_nh = baker.make(Person, ethnicity_source_value="NH", _using="research")
        baker.make(
            VisitOccurrence,
            person=person_nh,
            provider=self.provider,
            tier_id=self.tier.id,
            _using="research",
        )

        # Filter for NULL only
        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={"filters": {"person_demographics": {"ethnicity": ["__NULL__"]}}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_visit_search_null_filter_excludes_empty_strings(self):
        """Test that __NULL__ filter does not match empty string values."""
        self.authenticate_user()

        # Person with empty string gender (not NULL)
        self.person.gender_source_value = ""
        self.person.save(using="research")

        # Create person with actual NULL
        person_null = baker.make(Person, gender_source_value=None, _using="research")
        baker.make(
            VisitOccurrence,
            person=person_null,
            provider=self.provider,
            tier_id=self.tier.id,
            _using="research",
        )

        # Filter for NULL only
        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={"filters": {"person_demographics": {"gender": ["__NULL__"]}}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return the NULL record, not the empty string record
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["patient_id"], person_null.id)

    def test_visit_search_filter_by_age_range(self):
        """Test filtering by year of birth range (age)."""
        self.authenticate_user()

        # Set up person born in 1990
        self.person.year_of_birth = 1990
        self.person.save(using="research")

        # Create person born in 1950
        person_older = baker.make(Person, year_of_birth=1950, _using="research")
        baker.make(
            VisitOccurrence,
            person=person_older,
            provider=self.provider,
            tier_id=self.tier.id,
            _using="research",
        )

        # Filter for people born after 1980
        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={"filters": {"person_demographics": {"year_of_birth_from": 1980}}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)


class VisitSearchProviderDemographicFilteringTest(BaseResearchAPITestCase):
    """Test provider demographic filtering."""

    def test_visit_search_filter_by_provider_gender(self):
        """Test filtering by provider gender."""
        self.authenticate_user()

        # Set up provider with known gender
        self.provider.gender_source_value = "F"
        self.provider.save(using="research")

        # Create visit with different provider gender
        provider_m = baker.make(Provider, gender_source_value="M", _using="research")
        person2 = baker.make(Person, _using="research")
        baker.make(
            VisitOccurrence,
            person=person2,
            provider=provider_m,
            tier_id=self.tier.id,
            _using="research",
        )

        # Filter for Female provider only
        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={"filters": {"provider_demographics": {"gender": ["F"]}}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_visit_search_filter_by_provider_null_gender(self):
        """Test filtering provider with __NULL__ returns visits with NULL provider gender."""
        self.authenticate_user()

        # Set up provider with NULL gender
        self.provider.gender_source_value = None
        self.provider.save(using="research")

        # Create visit with provider that has gender
        provider_m = baker.make(Provider, gender_source_value="M", _using="research")
        person2 = baker.make(Person, _using="research")
        baker.make(
            VisitOccurrence,
            person=person2,
            provider=provider_m,
            tier_id=self.tier.id,
            _using="research",
        )

        # Filter for NULL provider gender
        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={"filters": {"provider_demographics": {"gender": ["__NULL__"]}}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_visit_search_filter_by_provider_race(self):
        """Test filtering by provider race."""
        self.authenticate_user()

        # Set up provider with known race
        self.provider.race_source_value = "A"
        self.provider.save(using="research")

        # Create visit with different provider race
        provider_w = baker.make(Provider, race_source_value="W", _using="research")
        person2 = baker.make(Person, _using="research")
        baker.make(
            VisitOccurrence,
            person=person2,
            provider=provider_w,
            tier_id=self.tier.id,
            _using="research",
        )

        # Filter for Asian provider only
        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={"filters": {"provider_demographics": {"race": ["A"]}}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_visit_search_filter_by_provider_ethnicity(self):
        """Test filtering by provider ethnicity."""
        self.authenticate_user()

        # Set up provider with known ethnicity
        self.provider.ethnicity_source_value = "H"
        self.provider.save(using="research")

        # Create visit with different provider ethnicity
        provider_nh = baker.make(Provider, ethnicity_source_value="NH", _using="research")
        person2 = baker.make(Person, _using="research")
        baker.make(
            VisitOccurrence,
            person=person2,
            provider=provider_nh,
            tier_id=self.tier.id,
            _using="research",
        )

        # Filter for Hispanic provider only
        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={"filters": {"provider_demographics": {"ethnicity": ["H"]}}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_visit_search_filter_by_provider_null_race(self):
        """Test filtering provider with __NULL__ returns visits with NULL provider race."""
        self.authenticate_user()

        # Set up provider with NULL race
        self.provider.race_source_value = None
        self.provider.save(using="research")

        # Create visit with provider that has race
        provider_w = baker.make(Provider, race_source_value="W", _using="research")
        person2 = baker.make(Person, _using="research")
        baker.make(
            VisitOccurrence,
            person=person2,
            provider=provider_w,
            tier_id=self.tier.id,
            _using="research",
        )

        # Filter for NULL provider race
        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={"filters": {"provider_demographics": {"race": ["__NULL__"]}}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_visit_search_filter_by_provider_null_ethnicity(self):
        """Test filtering provider with __NULL__ returns visits with NULL provider ethnicity."""
        self.authenticate_user()

        # Set up provider with NULL ethnicity
        self.provider.ethnicity_source_value = None
        self.provider.save(using="research")

        # Create visit with provider that has ethnicity
        provider_nh = baker.make(Provider, ethnicity_source_value="NH", _using="research")
        person2 = baker.make(Person, _using="research")
        baker.make(
            VisitOccurrence,
            person=person2,
            provider=provider_nh,
            tier_id=self.tier.id,
            _using="research",
        )

        # Filter for NULL provider ethnicity
        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={"filters": {"provider_demographics": {"ethnicity": ["__NULL__"]}}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)


class VisitSearchCombinedFiltersTest(BaseResearchAPITestCase):
    """Test combined filtering scenarios."""

    def test_visit_search_combined_person_and_provider_filters(self):
        """Test combining person and provider demographic filters."""
        self.authenticate_user()

        # Set up base visit: Male patient, Female provider
        self.person.gender_source_value = "M"
        self.person.save(using="research")
        self.provider.gender_source_value = "F"
        self.provider.save(using="research")

        # Create visit: Female patient, Female provider (should match)
        person_f = baker.make(Person, gender_source_value="F", _using="research")
        baker.make(
            VisitOccurrence,
            person=person_f,
            provider=self.provider,
            tier_id=self.tier.id,
            _using="research",
        )

        # Create visit: Male patient, Male provider (should not match)
        provider_m = baker.make(Provider, gender_source_value="M", _using="research")
        person_m2 = baker.make(Person, gender_source_value="M", _using="research")
        baker.make(
            VisitOccurrence,
            person=person_m2,
            provider=provider_m,
            tier_id=self.tier.id,
            _using="research",
        )

        # Filter for Male patient AND Female provider
        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={
                "filters": {
                    "person_demographics": {"gender": ["M"]},
                    "provider_demographics": {"gender": ["F"]},
                }
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_visit_search_combined_visit_and_demographic_filters(self):
        """Test combining visit filters with demographic filters."""
        self.authenticate_user()

        # Set up base visit
        self.person.gender_source_value = "M"
        self.person.save(using="research")
        self.visit.visit_source_value = "clinic"
        self.visit.save(using="research")

        # Create visit: Male patient, sim_center
        person_m = baker.make(Person, gender_source_value="M", _using="research")
        baker.make(
            VisitOccurrence,
            person=person_m,
            provider=self.provider,
            tier_id=self.tier.id,
            visit_source_value="sim_center",
            _using="research",
        )

        # Filter for Male patient AND clinic source
        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={
                "filters": {
                    "visit": {"visit_source_value": ["clinic"]},
                    "person_demographics": {"gender": ["M"]},
                }
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)


class VisitSearchSortingPaginationTest(BaseResearchAPITestCase):
    """Test sorting and pagination."""

    def test_visit_search_default_sorting(self):
        """Test that default sorting is by visit_start_date descending."""
        self.authenticate_user()

        # Set dates on visits
        self.visit.visit_start_date = date(2024, 1, 1)
        self.visit.save(using="research")

        person2 = baker.make(Person, _using="research")
        visit2 = baker.make(
            VisitOccurrence,
            person=person2,
            provider=self.provider,
            tier_id=self.tier.id,
            visit_start_date=date(2024, 6, 1),
            _using="research",
        )

        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={"filters": {}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        # Newer visit should be first (descending)
        self.assertEqual(results[0]["visit_id"], visit2.id)

    def test_visit_search_custom_sorting(self):
        """Test custom sort field and direction."""
        self.authenticate_user()

        # Set dates on visits
        self.visit.visit_start_date = date(2024, 1, 1)
        self.visit.save(using="research")

        person2 = baker.make(Person, _using="research")
        baker.make(
            VisitOccurrence,
            person=person2,
            provider=self.provider,
            tier_id=self.tier.id,
            visit_start_date=date(2024, 6, 1),
            _using="research",
        )

        # Sort ascending
        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={
                "filters": {},
                "sort": {"field": "visit_start_date", "direction": "asc"},
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        # Older visit should be first (ascending)
        self.assertEqual(results[0]["visit_id"], self.visit.id)

    def test_visit_search_pagination(self):
        """Test that pagination metadata is returned."""
        self.authenticate_user()

        # Create multiple visits
        for _ in range(5):
            person = baker.make(Person, _using="research")
            baker.make(
                VisitOccurrence,
                person=person,
                provider=self.provider,
                tier_id=self.tier.id,
                _using="research",
            )

        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={"filters": {}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 6)  # 1 from setUp + 5 new

    def test_visit_search_returns_active_filter_count(self):
        """Test that active filter count is returned in metadata."""
        self.authenticate_user()

        response = self.client.post(
            "/api/v1/research/private/visits-search/",
            data={
                "filters": {
                    "visit": {"tier_id": [1]},
                    "person_demographics": {"gender": ["M"]},
                }
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("filter_summary", response.data)
        self.assertIn("active_filters", response.data["filter_summary"])
        self.assertEqual(response.data["filter_summary"]["active_filters"], 2)
