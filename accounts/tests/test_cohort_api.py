"""
Tests for Cohort API endpoints.
Comprehensive test coverage for CRUD operations, duplicate action, and user isolation.
"""

from django.contrib.auth import get_user_model

from rest_framework import status

from accounts.models import Cohort

from .base import BaseTestCase

User = get_user_model()


class CohortModelTest(BaseTestCase):
    """Test cases for Cohort model functionality."""

    def test_cohort_creation_with_all_fields(self):
        """Test creating a cohort with all fields."""
        cohort = Cohort.objects.using("accounts").create(
            user=self.user,
            name="Test Cohort",
            description="Test description",
            filters={
                "visit": {"visit_type": ["Inpatient"]},
                "person": {"age_min": 18},
                "provider": {},
                "clinical": {},
            },
            visit_count=42,
        )

        self.assertEqual(cohort.name, "Test Cohort")
        self.assertEqual(cohort.description, "Test description")
        self.assertEqual(cohort.user, self.user)
        self.assertEqual(cohort.visit_count, 42)
        self.assertIsNotNone(cohort.created_at)
        self.assertIsNotNone(cohort.updated_at)

    def test_cohort_str_representation(self):
        """Test the string representation of a cohort."""
        cohort = Cohort.objects.using("accounts").create(
            user=self.user,
            name="Test Cohort",
            description="",
            filters={},
            visit_count=100,
        )

        expected = f"Test Cohort (100 visits) - {self.user.username}"
        self.assertEqual(str(cohort), expected)

    def test_cohort_cascade_delete_on_user_delete(self):
        """Test that cohorts are deleted when user is deleted."""
        cohort = Cohort.objects.using("accounts").create(
            user=self.user,
            name="Test Cohort",
            description="",
            filters={},
            visit_count=0,
        )
        cohort_id = cohort.id

        # Delete user
        self.user.delete(using="accounts")

        # Verify cohort was deleted
        with self.assertRaises(Cohort.DoesNotExist):
            Cohort.objects.using("accounts").get(id=cohort_id)

    def test_cohort_default_ordering(self):
        """Test that cohorts are ordered by -created_at by default."""
        cohort1 = Cohort.objects.using("accounts").create(
            user=self.user, name="First", description="", filters={}, visit_count=0
        )
        cohort2 = Cohort.objects.using("accounts").create(
            user=self.user, name="Second", description="", filters={}, visit_count=0
        )
        cohort3 = Cohort.objects.using("accounts").create(
            user=self.user, name="Third", description="", filters={}, visit_count=0
        )

        cohorts = list(Cohort.objects.using("accounts").filter(user=self.user))

        # Newest first
        self.assertEqual(cohorts[0].name, "Third")
        self.assertEqual(cohorts[1].name, "Second")
        self.assertEqual(cohorts[2].name, "First")

    def test_cohort_json_field_storage(self):
        """Test that filters are stored correctly as JSON."""
        complex_filters = {
            "visit": {
                "visit_type": ["Inpatient", "Emergency"],
                "date_range": {"start": "2020-01-01", "end": "2023-12-31"},
            },
            "person": {"age_min": 18, "age_max": 65, "gender": ["Male"]},
            "provider": {"specialty": ["Cardiology"]},
            "clinical": {"conditions": ["Diabetes"]},
        }

        cohort = Cohort.objects.using("accounts").create(
            user=self.user,
            name="Complex Filters",
            description="",
            filters=complex_filters,
            visit_count=0,
        )

        # Retrieve and verify
        saved_cohort = Cohort.objects.using("accounts").get(id=cohort.id)
        self.assertEqual(saved_cohort.filters, complex_filters)


class CohortAuthenticationTest(BaseTestCase):
    """Test cases for authentication requirements."""

    def test_list_cohorts_unauthenticated(self):
        """Test that unauthenticated requests to list endpoint return 401."""
        response = self.client.get("/api/v1/accounts/cohorts/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_cohort_detail_unauthenticated(self):
        """Test that unauthenticated requests to detail endpoint return 401."""
        cohort = Cohort.objects.using("accounts").create(
            user=self.user, name="Test", description="", filters={}, visit_count=0
        )
        response = self.client.get(f"/api/v1/accounts/cohorts/{cohort.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_cohort_unauthenticated(self):
        """Test that unauthenticated POST requests return 401."""
        data = {
            "name": "Test Cohort",
            "filters": {},
            "visit_count": 0,
        }
        response = self.client.post("/api/v1/accounts/cohorts/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_cohort_unauthenticated(self):
        """Test that unauthenticated PATCH requests return 401."""
        cohort = Cohort.objects.using("accounts").create(
            user=self.user, name="Test", description="", filters={}, visit_count=0
        )
        data = {"name": "Updated Name"}
        response = self.client.patch(f"/api/v1/accounts/cohorts/{cohort.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_cohort_unauthenticated(self):
        """Test that unauthenticated DELETE requests return 401."""
        cohort = Cohort.objects.using("accounts").create(
            user=self.user, name="Test", description="", filters={}, visit_count=0
        )
        response = self.client.delete(f"/api/v1/accounts/cohorts/{cohort.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_duplicate_cohort_unauthenticated(self):
        """Test that unauthenticated duplicate requests return 401."""
        cohort = Cohort.objects.using("accounts").create(
            user=self.user, name="Test", description="", filters={}, visit_count=0
        )
        response = self.client.post(f"/api/v1/accounts/cohorts/{cohort.id}/duplicate/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CohortListTest(BaseTestCase):
    """Test cases for listing cohorts."""

    def test_list_cohorts_authenticated(self):
        """Test listing cohorts for authenticated user."""
        self.authenticate_user()

        # Create cohorts
        for i in range(3):
            Cohort.objects.using("accounts").create(
                user=self.user,
                name=f"Cohort {i}",
                description="",
                filters={},
                visit_count=0,
            )

        response = self.client.get("/api/v1/accounts/cohorts/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(len(response.data["cohorts"]), 3)

    def test_list_cohorts_empty(self):
        """Test listing cohorts when user has none."""
        self.authenticate_user()

        response = self.client.get("/api/v1/accounts/cohorts/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(len(response.data["cohorts"]), 0)

    def test_list_cohorts_user_isolation(self):
        """Test that users only see their own cohorts."""
        self.authenticate_user()

        # Create cohorts for current user
        Cohort.objects.using("accounts").create(
            user=self.user, name="My Cohort", description="", filters={}, visit_count=0
        )

        # Create cohorts for another user
        other_user = User.objects.db_manager("accounts").create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        for i in range(2):
            Cohort.objects.using("accounts").create(
                user=other_user,
                name=f"Other Cohort {i}",
                description="",
                filters={},
                visit_count=0,
            )

        response = self.client.get("/api/v1/accounts/cohorts/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["cohorts"][0]["name"], "My Cohort")

    def test_list_cohorts_ordering(self):
        """Test that cohorts are ordered by creation date (newest first)."""
        self.authenticate_user()

        cohort1 = Cohort.objects.using("accounts").create(
            user=self.user, name="First", description="", filters={}, visit_count=0
        )
        cohort2 = Cohort.objects.using("accounts").create(
            user=self.user, name="Second", description="", filters={}, visit_count=0
        )
        cohort3 = Cohort.objects.using("accounts").create(
            user=self.user, name="Third", description="", filters={}, visit_count=0
        )

        response = self.client.get("/api/v1/accounts/cohorts/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Newest first
        self.assertEqual(response.data["cohorts"][0]["name"], "Third")
        self.assertEqual(response.data["cohorts"][1]["name"], "Second")
        self.assertEqual(response.data["cohorts"][2]["name"], "First")

    def test_list_cohorts_includes_filters(self):
        """Test that list response includes filters field for display."""
        self.authenticate_user()

        cohort = Cohort.objects.using("accounts").create(
            user=self.user,
            name="Test",
            description="",
            filters={
                "visit": {"visit_type": ["Inpatient"]},
                "person_demographics": {"age_min": 18},
                "provider_demographics": {},
                "clinical": {},
            },
            visit_count=0,
        )

        response = self.client.get("/api/v1/accounts/cohorts/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cohort_data = response.data["cohorts"][0]
        self.assertIn("filters", cohort_data)
        self.assertIn("visit", cohort_data["filters"])
        self.assertIn("person_demographics", cohort_data["filters"])
        self.assertIn("provider_demographics", cohort_data["filters"])
        self.assertIn("clinical", cohort_data["filters"])


class CohortCreateTest(BaseTestCase):
    """Test cases for creating cohorts."""

    def test_create_cohort_with_valid_data(self):
        """Test creating a cohort with valid data."""
        self.authenticate_user()

        data = {
            "name": "New Cohort",
            "description": "A test cohort",
            "filters": {
                "visit": {"visit_type": ["Inpatient"]},
                "person_demographics": {},
                "provider_demographics": {},
                "clinical": {},
            },
            "visit_count": 50,
        }

        response = self.client.post("/api/v1/accounts/cohorts/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Cohort")
        self.assertEqual(response.data["description"], "A test cohort")
        self.assertEqual(response.data["visit_count"], 50)
        self.assertIsNotNone(response.data["id"])
        self.assertIsNotNone(response.data["created_at"])
        self.assertIsNotNone(response.data["updated_at"])

    def test_create_cohort_minimal_data(self):
        """Test creating a cohort with minimal required data (no description)."""
        self.authenticate_user()

        data = {
            "name": "Minimal Cohort",
            "filters": {},
            "visit_count": 0,
        }

        response = self.client.post("/api/v1/accounts/cohorts/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Minimal Cohort")
        self.assertEqual(response.data["description"], "")

    def test_create_cohort_auto_assigns_user(self):
        """Test that cohort is automatically assigned to the authenticated user."""
        self.authenticate_user()

        data = {
            "name": "User Test Cohort",
            "filters": {},
            "visit_count": 0,
        }

        response = self.client.post("/api/v1/accounts/cohorts/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify in database
        cohort = Cohort.objects.using("accounts").get(id=response.data["id"])
        self.assertEqual(cohort.user, self.user)

    def test_create_cohort_missing_required_fields(self):
        """Test that creating a cohort without required fields returns 400."""
        self.authenticate_user()

        # Missing name
        data = {"filters": {}, "visit_count": 0}
        response = self.client.post("/api/v1/accounts/cohorts/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Missing filters
        data = {"name": "Test", "visit_count": 0}
        response = self.client.post("/api/v1/accounts/cohorts/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Missing visit_count
        data = {"name": "Test", "filters": {}}
        response = self.client.post("/api/v1/accounts/cohorts/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CohortRetrieveTest(BaseTestCase):
    """Test cases for retrieving cohort details."""

    def test_get_cohort_detail_authenticated(self):
        """Test retrieving cohort detail for authenticated user."""
        self.authenticate_user()

        cohort = Cohort.objects.using("accounts").create(
            user=self.user,
            name="Detail Cohort",
            description="Test description",
            filters={},
            visit_count=100,
        )

        response = self.client.get(f"/api/v1/accounts/cohorts/{cohort.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], cohort.id)
        self.assertEqual(response.data["name"], "Detail Cohort")
        self.assertEqual(response.data["description"], "Test description")
        self.assertEqual(response.data["visit_count"], 100)

    def test_get_cohort_detail_not_found(self):
        """Test 404 for non-existent cohort ID."""
        self.authenticate_user()

        response = self.client.get("/api/v1/accounts/cohorts/99999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_cohort_detail_other_user(self):
        """Test that user cannot access another user's cohort."""
        self.authenticate_user()

        # Create cohort for another user
        other_user = User.objects.db_manager("accounts").create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        other_cohort = Cohort.objects.using("accounts").create(
            user=other_user, name="Other", description="", filters={}, visit_count=0
        )

        response = self.client.get(f"/api/v1/accounts/cohorts/{other_cohort.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CohortUpdateTest(BaseTestCase):
    """Test cases for updating cohorts."""

    def test_update_cohort_name(self):
        """Test updating cohort name via PATCH."""
        self.authenticate_user()

        cohort = Cohort.objects.using("accounts").create(
            user=self.user, name="Original Name", description="", filters={}, visit_count=0
        )

        data = {"name": "Updated Name"}
        response = self.client.patch(f"/api/v1/accounts/cohorts/{cohort.id}/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Name")

        # Verify in database
        cohort.refresh_from_db(using="accounts")
        self.assertEqual(cohort.name, "Updated Name")

    def test_update_cohort_other_user(self):
        """Test that user cannot update another user's cohort."""
        self.authenticate_user()

        # Create cohort for another user
        other_user = User.objects.db_manager("accounts").create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        other_cohort = Cohort.objects.using("accounts").create(
            user=other_user, name="Original", description="", filters={}, visit_count=0
        )

        data = {"name": "Hacked Name"}
        response = self.client.patch(
            f"/api/v1/accounts/cohorts/{other_cohort.id}/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Verify cohort was not updated
        other_cohort.refresh_from_db(using="accounts")
        self.assertNotEqual(other_cohort.name, "Hacked Name")


class CohortDeleteTest(BaseTestCase):
    """Test cases for deleting cohorts."""

    def test_delete_cohort_authenticated(self):
        """Test deleting own cohort."""
        self.authenticate_user()

        cohort = Cohort.objects.using("accounts").create(
            user=self.user, name="Test", description="", filters={}, visit_count=0
        )
        cohort_id = cohort.id

        response = self.client.delete(f"/api/v1/accounts/cohorts/{cohort_id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify cohort was deleted
        with self.assertRaises(Cohort.DoesNotExist):
            Cohort.objects.using("accounts").get(id=cohort_id)

    def test_delete_cohort_other_user(self):
        """Test that user cannot delete another user's cohort."""
        self.authenticate_user()

        # Create cohort for another user
        other_user = User.objects.db_manager("accounts").create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        other_cohort = Cohort.objects.using("accounts").create(
            user=other_user, name="Other", description="", filters={}, visit_count=0
        )

        response = self.client.delete(f"/api/v1/accounts/cohorts/{other_cohort.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Verify cohort still exists
        self.assertTrue(Cohort.objects.using("accounts").filter(id=other_cohort.id).exists())


class CohortDuplicateTest(BaseTestCase):
    """Test cases for duplicating cohorts."""

    def test_duplicate_cohort_default_name(self):
        """Test duplicating a cohort with default name."""
        self.authenticate_user()

        original = Cohort.objects.using("accounts").create(
            user=self.user,
            name="Original Cohort",
            description="Original description",
            filters={"visit": {"visit_type": ["Inpatient"]}},
            visit_count=50,
        )

        response = self.client.post(
            f"/api/v1/accounts/cohorts/{original.id}/duplicate/", format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Copy of Original Cohort")
        self.assertEqual(response.data["description"], "Original description")
        self.assertEqual(response.data["filters"], original.filters)
        self.assertEqual(response.data["visit_count"], 50)
        self.assertNotEqual(response.data["id"], original.id)

    def test_duplicate_cohort_custom_name(self):
        """Test duplicating a cohort with custom name."""
        self.authenticate_user()

        original = Cohort.objects.using("accounts").create(
            user=self.user, name="Original", description="", filters={}, visit_count=0
        )

        data = {"name": "Custom Duplicate Name"}
        response = self.client.post(
            f"/api/v1/accounts/cohorts/{original.id}/duplicate/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Custom Duplicate Name")

    def test_duplicate_cohort_other_user(self):
        """Test that user cannot duplicate another user's cohort."""
        self.authenticate_user()

        # Create cohort for another user
        other_user = User.objects.db_manager("accounts").create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        other_cohort = Cohort.objects.using("accounts").create(
            user=other_user, name="Other", description="", filters={}, visit_count=0
        )

        response = self.client.post(
            f"/api/v1/accounts/cohorts/{other_cohort.id}/duplicate/", format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
