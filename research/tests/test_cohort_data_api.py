"""
Tests for Cohort Data API endpoint.
Tests fetching all OMOP table data filtered by cohort criteria.
"""

from django.contrib.auth import get_user_model

from model_bakery import baker
from rest_framework import status

from accounts.models import Cohort
from research.models import (
    ConditionOccurrence,
    DrugExposure,
    Measurement,
    Note,
    Observation,
    ProcedureOccurrence,
    VisitOccurrence,
)

from .test_base import BaseResearchAPITestCase

User = get_user_model()


class CohortDataViewSetTest(BaseResearchAPITestCase):
    """Test cases for cohort data API endpoint."""

    def setUp(self):
        """Set up test data with cohort and OMOP tables."""
        super().setUp()

        # Create cohort with basic filters
        self.cohort = baker.make(
            Cohort,
            user=self.user,
            name="Test Cohort",
            description="Test cohort description",
            filters={"visit": {"tier_id": [1]}},  # Filter for tier 1 visits
            visit_count=1,
            _using="accounts",
        )

        # Create related OMOP data
        self.condition = baker.make(
            ConditionOccurrence,
            visit_occurrence=self.visit,
            condition_source_value="Hypertension",
            _using="research",
        )

        self.drug = baker.make(
            DrugExposure,
            visit_occurrence=self.visit,
            description="Aspirin",
            _using="research",
        )

        self.procedure = baker.make(
            ProcedureOccurrence,
            visit_occurrence=self.visit,
            name="Blood Test",
            _using="research",
        )

        self.measurement = baker.make(
            Measurement, visit_occurrence=self.visit, bp_systolic=120, _using="research"
        )

        self.observation = baker.make(
            Observation,
            visit_occurrence=self.visit,
            file_type="patient_view",
            _using="research",
        )

        self.note = baker.make(
            Note,
            visit_occurrence=self.visit,
            note_text="Patient doing well",
            _using="research",
        )

        self.url = f"/api/v1/research/private/cohorts/{self.cohort.id}/data/"

    # ============================================================================
    # Authentication & Authorization Tests
    # ============================================================================

    def test_unauthenticated_user_cannot_access(self):
        """Unauthenticated requests should return 401."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_view_own_cohort_data(self):
        """User can view their own cohort's data."""
        self.authenticate_user()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_view_other_users_cohort(self):
        """User cannot view another user's cohort data."""
        # Create another user and their cohort
        other_user = baker.make(User, username="otheruser", _using="accounts")
        other_cohort = baker.make(
            Cohort,
            user=other_user,
            name="Other Cohort",
            filters={},
            visit_count=0,
            _using="accounts",
        )

        self.authenticate_user()
        url = f"/api/v1/research/private/cohorts/{other_cohort.id}/data/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("permission", response.json()["detail"].lower())

    def test_nonexistent_cohort_returns_404(self):
        """Request for non-existent cohort should return 404."""
        self.authenticate_user()
        url = "/api/v1/research/private/cohorts/99999/data/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ============================================================================
    # Data Structure Tests
    # ============================================================================

    def test_response_has_correct_omop_tables(self):
        """Response should contain all OMOP table fields."""
        self.authenticate_user()
        response = self.client.get(self.url)
        data = response.json()

        # Verify all expected OMOP tables are present
        expected_tables = [
            "persons",
            "providers",
            "visits",
            "conditions",
            "drugs",
            "procedures",
            "measurements",
            "observations",
            "notes",
            "patient_surveys",
            "provider_surveys",
            "audit_logs",
            "concepts",
            "_metadata",
        ]

        for table in expected_tables:
            self.assertIn(table, data, f"Missing table: {table}")

    def test_response_matches_sample_data_format(self):
        """Response structure should match SampleDataAPIResponse format."""
        self.authenticate_user()
        response = self.client.get(self.url)
        data = response.json()

        # Verify each table is a list
        for table in ["persons", "providers", "visits", "conditions", "drugs"]:
            self.assertIsInstance(data[table], list, f"{table} should be a list")

        # Verify metadata structure
        self.assertIn("_metadata", data)
        metadata = data["_metadata"]
        self.assertIn("description", metadata)
        self.assertIn("source", metadata)
        self.assertIn("count", metadata)
        self.assertEqual(metadata["source"], "cohort_filter")

    def test_metadata_contains_correct_counts(self):
        """Metadata should contain correct visit/person/provider counts."""
        self.authenticate_user()
        response = self.client.get(self.url)
        data = response.json()

        metadata = data["_metadata"]
        counts = metadata["count"]

        self.assertEqual(counts["visits"], 1)
        self.assertEqual(counts["persons"], 1)
        self.assertEqual(counts["providers"], 1)

    def test_empty_cohort_returns_empty_tables(self):
        """Cohort with no matching visits should return empty arrays."""
        # Create cohort with filters that match no visits
        empty_cohort = baker.make(
            Cohort,
            user=self.user,
            name="Empty Cohort",
            filters={"visit": {"tier_id": [999]}},  # Non-existent tier
            visit_count=0,
            _using="accounts",
        )

        self.authenticate_user()
        url = f"/api/v1/research/private/cohorts/{empty_cohort.id}/data/"
        response = self.client.get(url)
        data = response.json()

        # All tables should be empty
        self.assertEqual(len(data["visits"]), 0)
        self.assertEqual(len(data["persons"]), 0)
        self.assertEqual(len(data["providers"]), 0)
        self.assertEqual(len(data["conditions"]), 0)
        self.assertEqual(data["_metadata"]["count"]["visits"], 0)

    # ============================================================================
    # Filtering Tests
    # ============================================================================

    def test_visit_filters_applied_correctly(self):
        """Cohort's visit filters should be applied correctly."""
        self.authenticate_user()
        response = self.client.get(self.url)
        data = response.json()

        # Should return 1 visit (tier 1)
        self.assertEqual(len(data["visits"]), 1)
        self.assertEqual(data["visits"][0]["tier_id"], 1)

    def test_tier_access_control_enforced(self):
        """User can only see visits within their tier level."""
        # Create visit with tier 2 (user has tier 1)
        tier2_visit = baker.make(
            VisitOccurrence,
            person=self.person,
            provider=self.provider,
            tier_id=2,
            _using="research",
        )

        # Create cohort that includes both tier 1 and tier 2
        multi_tier_cohort = baker.make(
            Cohort,
            user=self.user,
            name="Multi-Tier Cohort",
            filters={"visit": {"tier_id": [1, 2]}},
            visit_count=2,
            _using="accounts",
        )

        self.authenticate_user()
        url = f"/api/v1/research/private/cohorts/{multi_tier_cohort.id}/data/"
        response = self.client.get(url)
        data = response.json()

        # Should only see tier 1 visit (user's tier)
        self.assertEqual(len(data["visits"]), 1)
        self.assertEqual(data["visits"][0]["tier_id"], 1)

    # ============================================================================
    # Data Integrity Tests
    # ============================================================================

    def test_all_related_tables_populated(self):
        """All OMOP tables should have correct related data."""
        self.authenticate_user()
        response = self.client.get(self.url)
        data = response.json()

        # Verify related data is present
        self.assertGreater(len(data["persons"]), 0)
        self.assertGreater(len(data["providers"]), 0)
        self.assertGreater(len(data["visits"]), 0)
        self.assertGreater(len(data["conditions"]), 0)
        self.assertGreater(len(data["drugs"]), 0)
        self.assertGreater(len(data["procedures"]), 0)
        self.assertGreater(len(data["measurements"]), 0)
        self.assertGreater(len(data["observations"]), 0)
        self.assertGreater(len(data["notes"]), 0)

    def test_visit_ids_match_filter_criteria(self):
        """Returned visits should match cohort filter criteria."""
        self.authenticate_user()
        response = self.client.get(self.url)
        data = response.json()

        # All visits should have tier_id = 1 (from cohort filters)
        for visit in data["visits"]:
            self.assertEqual(visit["tier_id"], 1)

    def test_person_provider_ids_match_visits(self):
        """Person and Provider IDs should match those in returned visits."""
        self.authenticate_user()
        response = self.client.get(self.url)
        data = response.json()

        # Extract person and provider IDs from visits
        visit_person_ids = set(v["person_id"] for v in data["visits"])
        visit_provider_ids = set(v["provider_id"] for v in data["visits"])

        # Extract IDs from persons and providers tables
        person_ids = set(p["id"] for p in data["persons"])
        provider_ids = set(p["id"] for p in data["providers"])

        # Person/Provider tables should contain exactly the IDs from visits
        self.assertEqual(person_ids, visit_person_ids)
        self.assertEqual(provider_ids, visit_provider_ids)

    def test_clinical_data_linked_to_visits(self):
        """Clinical data (conditions, drugs, etc.) should be linked to returned visits."""
        self.authenticate_user()
        response = self.client.get(self.url)
        data = response.json()

        visit_ids = set(v["id"] for v in data["visits"])

        # All conditions should reference visits in the cohort
        for condition in data["conditions"]:
            self.assertIn(condition["visit_occurrence_id"], visit_ids)

        # All drugs should reference visits in the cohort
        for drug in data["drugs"]:
            self.assertIn(drug["visit_occurrence_id"], visit_ids)

        # All procedures should reference visits in the cohort
        for procedure in data["procedures"]:
            self.assertIn(procedure["visit_occurrence_id"], visit_ids)

    def test_metadata_description_includes_cohort_name(self):
        """Metadata description should include cohort name."""
        self.authenticate_user()
        response = self.client.get(self.url)
        data = response.json()

        description = data["_metadata"]["description"]
        self.assertIn(self.cohort.name, description)
        self.assertEqual(description, f"Cohort: {self.cohort.name}")

    # ============================================================================
    # Edge Cases
    # ============================================================================

    def test_cohort_with_empty_filters(self):
        """Cohort with empty filters should return all accessible visits."""
        # Create cohort with no filters
        no_filter_cohort = baker.make(
            Cohort,
            user=self.user,
            name="No Filter Cohort",
            filters={},
            visit_count=1,
            _using="accounts",
        )

        self.authenticate_user()
        url = f"/api/v1/research/private/cohorts/{no_filter_cohort.id}/data/"
        response = self.client.get(url)
        data = response.json()

        # Should return visits (at least the one we created in setUp)
        self.assertGreaterEqual(len(data["visits"]), 1)
