from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from model_bakery import baker
from rest_framework import status

from accounts.models import Agreement, AgreementType, UserAgreement

from .base import BaseTestCase

User = get_user_model()


class AgreementAPITest(BaseTestCase):
    """Test cases for agreement API endpoints."""

    def setUp(self):
        super().setUp()

        # Create agreement types
        self.data_use_type = baker.make(
            AgreementType,
            name="Data Use Agreement",
            description="Agreements for data usage",
            _using="accounts",
        )
        self.code_conduct_type = baker.make(
            AgreementType,
            name="Code of Conduct",
            description="Code of conduct agreements",
            _using="accounts",
        )

        # Create agreements
        self.agreement1 = baker.make(
            Agreement,
            agreement_type=self.data_use_type,
            title="PhysioNet Data Use Agreement",
            version="1.5.0",
            project_name="PhysioNet Cardiovascular Study",
            content="This is the data use agreement content...",
            _using="accounts",
        )

        self.agreement2 = baker.make(
            Agreement,
            agreement_type=self.data_use_type,
            title="MIT-BIH Database Agreement",
            version="2.1.0",
            project_name="MIT-BIH Arrhythmia Database",
            content="MIT-BIH database usage agreement...",
            _using="accounts",
        )

        self.agreement3 = baker.make(
            Agreement,
            agreement_type=self.code_conduct_type,
            title="Research Ethics Code",
            version="1.0.0",
            project_name="",  # No specific project
            content="Code of conduct for research ethics...",
            _using="accounts",
        )

        # Create user agreements (signed agreements)
        self.user_agreement1 = baker.make(
            UserAgreement,
            user=self.user,
            agreement=self.agreement1,
            signed_at=timezone.now(),
            is_active=True,
            _using="accounts",
        )

        self.user_agreement2 = baker.make(
            UserAgreement,
            user=self.user,
            agreement=self.agreement3,
            signed_at=timezone.now(),
            is_active=True,
            _using="accounts",
        )

    def test_get_user_agreements_authenticated(self):
        """Test retrieving user's signed agreements."""
        self.authenticate_user()
        url = "/api/v1/accounts/agreements/user-agreements/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)  # User has 2 signed agreements

        # Check agreement data structure (using UserAgreementListSerializer)
        agreement_data = response.data["results"][0]
        expected_fields = [
            "id",
            "agreement_title",
            "agreement_version",
            "agreement_type",
            "date_signed",
            "is_active",
        ]
        for field in expected_fields:
            self.assertIn(field, agreement_data)

        # Check specific agreement data (ordered by signed_at desc, so most recent first)
        # Since both agreements are created almost simultaneously, either could be first
        # Let's just verify we have the right types of data
        self.assertIn(
            agreement_data["agreement_title"],
            ["PhysioNet Data Use Agreement", "Research Ethics Code"],
        )
        self.assertIn(agreement_data["agreement_type"], ["Data Use Agreement", "Code of Conduct"])

    def test_get_user_agreements_unauthenticated(self):
        """Test retrieving agreements without authentication."""
        url = "/api/v1/accounts/agreements/user-agreements/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_specific_user_agreement(self):
        """Test retrieving a specific user agreement."""
        self.authenticate_user()
        url = f"/api/v1/accounts/agreements/user-agreements/{self.user_agreement1.id}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user_agreement1.id)
        self.assertEqual(response.data["agreement_title"], "PhysioNet Data Use Agreement")

    def test_get_user_agreements_grouped(self):
        """Test retrieving user agreements grouped by type."""
        self.authenticate_user()
        url = "/api/v1/accounts/agreements/user-agreements/grouped/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data_use_agreements", response.data)
        self.assertIn("code_of_conduct", response.data)

        # Check data use agreements
        data_use_agreements = response.data["data_use_agreements"]
        self.assertEqual(len(data_use_agreements), 1)  # User signed 1 data use agreement
        self.assertEqual(data_use_agreements[0]["name"], "PhysioNet Data Use Agreement")

        # Check code of conduct
        code_conduct = response.data["code_of_conduct"]
        self.assertEqual(len(code_conduct), 1)  # User signed 1 code of conduct
        self.assertEqual(code_conduct[0]["name"], "Research Ethics Code")

    def test_get_all_agreements(self):
        """Test retrieving all available agreements."""
        self.authenticate_user()
        url = "/api/v1/accounts/agreements/agreements/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)  # 3 total agreements created

        # Check agreement data structure (using AgreementSerializer)
        agreement_data = response.data["results"][0]
        expected_fields = [
            "id",
            "title",
            "version",
            "project_name",
            "agreement_type",
            "content",
            "created_at",
        ]
        for field in expected_fields:
            self.assertIn(field, agreement_data)

        # Check that agreement_type is nested object
        self.assertIn("name", agreement_data["agreement_type"])

    def test_get_specific_agreement(self):
        """Test retrieving a specific agreement."""
        self.authenticate_user()
        url = f"/api/v1/accounts/agreements/agreements/{self.agreement1.id}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.agreement1.id)
        self.assertEqual(response.data["title"], "PhysioNet Data Use Agreement")
        self.assertEqual(response.data["version"], "1.5.0")
        self.assertEqual(response.data["project_name"], "PhysioNet Cardiovascular Study")

    def test_user_agreements_ordered_by_signed_date(self):
        """Test that user agreements are ordered by signed date (most recent first)."""
        # Create another user agreement with earlier date
        import datetime

        earlier_date = timezone.now() - datetime.timedelta(days=1)

        baker.make(
            UserAgreement,
            user=self.user,
            agreement=self.agreement2,
            signed_at=earlier_date,
            is_active=True,
            _using="accounts",
        )

        self.authenticate_user()
        url = "/api/v1/accounts/agreements/user-agreements/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)  # Now 3 signed agreements

        # Check that agreements are ordered by signed_at descending
        signed_dates = [agreement["date_signed"] for agreement in response.data["results"]]
        self.assertEqual(signed_dates, sorted(signed_dates, reverse=True))

    def test_user_agreements_only_active(self):
        """Test that only active user agreements are returned."""
        # Create an inactive user agreement
        baker.make(
            UserAgreement,
            user=self.user,
            agreement=self.agreement2,
            signed_at=timezone.now(),
            is_active=False,  # This should not appear in results
            _using="accounts",
        )

        self.authenticate_user()
        url = "/api/v1/accounts/agreements/user-agreements/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)  # Still only 2 active agreements

        # Verify all returned agreements are active
        for agreement in response.data["results"]:
            self.assertTrue(agreement["is_active"])

    def test_user_can_only_see_own_agreements(self):
        """Test that users can only see their own signed agreements."""
        # Create another user with different agreements
        other_user = User.objects.db_manager("accounts").create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )

        baker.make(
            UserAgreement,
            user=other_user,
            agreement=self.agreement2,
            signed_at=timezone.now(),
            is_active=True,
            _using="accounts",
        )

        self.authenticate_user()
        url = "/api/v1/accounts/agreements/user-agreements/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)  # Only original user's agreements

        # Verify all agreements belong to the authenticated user (UserAgreementListSerializer doesn't include user field, but that's by design since we filter by user in queryset)
        # The fact that we only get 2 agreements (not 3 including other user's) proves the filtering works
        for agreement in response.data["results"]:
            # All returned agreements should be from the authenticated user
            self.assertTrue(agreement["is_active"])


class AgreementTypeModelTest(TestCase):
    """Test cases for AgreementType model."""

    databases = ["default", "accounts"]

    def test_agreement_type_str_representation(self):
        """Test the string representation of AgreementType."""
        agreement_type = baker.make(AgreementType, name="Test Agreement Type", _using="accounts")
        self.assertEqual(str(agreement_type), "Test Agreement Type")

    def test_agreement_type_unique_name(self):
        """Test that agreement type names are unique."""
        baker.make(AgreementType, name="Unique Name", _using="accounts")

        with self.assertRaises(Exception):
            baker.make(AgreementType, name="Unique Name", _using="accounts")


class AgreementModelTest(TestCase):
    """Test cases for Agreement model."""

    databases = ["default", "accounts"]

    def setUp(self):
        self.agreement_type = baker.make(AgreementType, name="Test Type", _using="accounts")

    def test_agreement_str_representation(self):
        """Test the string representation of Agreement."""
        agreement = baker.make(
            Agreement,
            agreement_type=self.agreement_type,
            title="Test Agreement",
            version="1.0.0",
            _using="accounts",
        )
        self.assertEqual(str(agreement), "Test Agreement v1.0.0")

    def test_agreement_with_project_name(self):
        """Test agreement with project name."""
        agreement = baker.make(
            Agreement,
            agreement_type=self.agreement_type,
            title="Project Agreement",
            version="2.0.0",
            project_name="Test Project",
            _using="accounts",
        )
        self.assertEqual(agreement.project_name, "Test Project")


class UserAgreementModelTest(TestCase):
    """Test cases for UserAgreement model."""

    databases = ["default", "accounts"]

    def setUp(self):
        self.user = User.objects.db_manager("accounts").create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.agreement_type = baker.make(AgreementType, name="Test Type", _using="accounts")
        self.agreement = baker.make(
            Agreement,
            agreement_type=self.agreement_type,
            title="Test Agreement",
            version="1.0.0",
            _using="accounts",
        )

    def test_user_agreement_str_representation(self):
        """Test the string representation of UserAgreement."""
        user_agreement = baker.make(
            UserAgreement, user=self.user, agreement=self.agreement, _using="accounts"
        )
        expected = f"{self.user.username} - Test Agreement"
        self.assertEqual(str(user_agreement), expected)

    def test_user_agreement_default_active(self):
        """Test that user agreements are active by default."""
        user_agreement = baker.make(
            UserAgreement, user=self.user, agreement=self.agreement, _using="accounts"
        )
        self.assertTrue(user_agreement.is_active)

    def test_user_agreement_auto_signed_at(self):
        """Test that signed_at is automatically set."""
        user_agreement = baker.make(
            UserAgreement, user=self.user, agreement=self.agreement, _using="accounts"
        )
        self.assertIsNotNone(user_agreement.signed_at)
        self.assertLessEqual(
            (timezone.now() - user_agreement.signed_at).total_seconds(),
            1,  # Should be within 1 second
        )
