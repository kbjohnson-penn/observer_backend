from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Organization, Profile, Tier

from .base import BaseTestCase

User = get_user_model()


class PasswordChangeAPITest(BaseTestCase):
    """Test cases for password change API endpoint."""

    def test_password_change_success(self):
        """Test successful password change with valid old password."""
        self.authenticate_user()
        url = "/api/v1/accounts/auth/change-password/"
        data = {
            "old_password": "testpass123",
            "new_password": "NewSecurePassword123!",
            "new_password_confirm": "NewSecurePassword123!",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)
        self.assertEqual(
            response.data["detail"],
            "Password updated successfully. Please log in again with your new password.",
        )

        # Verify logout_required flag is set for security
        self.assertTrue(response.data.get("logout_required"))

        # Verify cookies are cleared
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
        # Cookies should be deleted (empty value with max_age=0 or expires in past)
        access_cookie = response.cookies.get("access_token")
        refresh_cookie = response.cookies.get("refresh_token")
        # Check that cookies are being cleared (value is empty or max_age is 0)
        self.assertTrue(
            access_cookie.value == "" or access_cookie["max-age"] == 0,
            "Access token cookie should be cleared",
        )
        self.assertTrue(
            refresh_cookie.value == "" or refresh_cookie["max-age"] == 0,
            "Refresh token cookie should be cleared",
        )

        # Verify the password was actually changed
        self.user.refresh_from_db(using="accounts")
        self.assertTrue(self.user.check_password("NewSecurePassword123!"))
        self.assertFalse(self.user.check_password("testpass123"))

    def test_password_change_wrong_old_password(self):
        """Test password change with incorrect old password."""
        self.authenticate_user()
        url = "/api/v1/accounts/auth/change-password/"
        data = {
            "old_password": "wrongpassword",
            "new_password": "NewSecurePassword123!",
            "new_password_confirm": "NewSecurePassword123!",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("old_password", response.data)
        self.assertEqual(response.data["old_password"], ["Current password is incorrect."])

    def test_password_change_password_mismatch(self):
        """Test password change with mismatched new passwords."""
        self.authenticate_user()
        url = "/api/v1/accounts/auth/change-password/"
        data = {
            "old_password": "testpass123",
            "new_password": "NewSecurePassword123!",
            "new_password_confirm": "DifferentPassword123!",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Errors are nested under 'errors' key in the response
        self.assertIn("errors", response.data)
        self.assertIn("new_password_confirm", response.data["errors"])

    def test_password_change_weak_password(self):
        """Test password change with weak new password."""
        self.authenticate_user()
        url = "/api/v1/accounts/auth/change-password/"
        data = {
            "old_password": "testpass123",
            "new_password": "weak",  # Too short
            "new_password_confirm": "weak",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Errors are nested under 'errors' key in the response
        self.assertIn("errors", response.data)
        self.assertIn("new_password", response.data["errors"])
        # Django's MinimumLengthValidator message (configured for 12 chars in settings)
        self.assertIn(
            "This password is too short. It must contain at least 12 characters.",
            str(response.data["errors"]["new_password"]),
        )

    def test_password_change_unauthenticated(self):
        """Test password change without authentication."""
        url = "/api/v1/accounts/auth/change-password/"
        data = {
            "old_password": "testpass123",
            "new_password": "NewSecurePassword123!",
            "new_password_confirm": "NewSecurePassword123!",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_change_missing_fields(self):
        """Test password change with missing required fields."""
        self.authenticate_user()
        url = "/api/v1/accounts/auth/change-password/"
        data = {
            "old_password": "testpass123"
            # Missing new passwords
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Errors are nested under 'errors' key in the response
        self.assertIn("errors", response.data)
        self.assertIn("new_password", response.data["errors"])
        self.assertIn("new_password_confirm", response.data["errors"])

    def test_password_change_rate_limiting(self):
        """Test that password change endpoint is rate limited."""
        # Skip this test as rate limiting interferes with other tests
        # In production, rate limiting is important but in tests it causes issues
        self.skipTest("Rate limiting test skipped to avoid interference with other tests")

    def test_password_change_blacklists_all_tokens(self):
        """Test that password change blacklists all outstanding refresh tokens."""
        # Create multiple refresh tokens (simulating multiple devices/sessions)
        token1 = RefreshToken.for_user(self.user)
        token2 = RefreshToken.for_user(self.user)
        token3 = RefreshToken.for_user(self.user)

        # Verify tokens are created
        outstanding_tokens_before = OutstandingToken.objects.using("accounts").filter(
            user=self.user
        )
        self.assertGreaterEqual(outstanding_tokens_before.count(), 3)

        # Authenticate and change password
        self.authenticate_user()
        url = "/api/v1/accounts/auth/change-password/"
        data = {
            "old_password": "testpass123",
            "new_password": "NewSecurePassword123!",
            "new_password_confirm": "NewSecurePassword123!",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify all tokens are blacklisted
        outstanding_tokens_after = OutstandingToken.objects.using("accounts").filter(user=self.user)
        for token in outstanding_tokens_after:
            # Each token should have a corresponding BlacklistedToken entry
            try:
                # Try to access the blacklisted token - will raise DoesNotExist if not blacklisted
                token.blacklistedtoken
                # If we get here, token is blacklisted
                blacklisted = True
            except Exception:
                blacklisted = False

            self.assertTrue(
                blacklisted,
                f"Token {token.id} should be blacklisted after password change",
            )

    def test_password_change_invalidates_all_sessions(self):
        """Test that old tokens cannot be used after password change."""
        # Create refresh tokens before password change
        old_refresh1 = RefreshToken.for_user(self.user)
        old_refresh2 = RefreshToken.for_user(self.user)

        # Change password
        self.authenticate_user()
        url = "/api/v1/accounts/auth/change-password/"
        data = {
            "old_password": "testpass123",
            "new_password": "NewSecurePassword123!",
            "new_password_confirm": "NewSecurePassword123!",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Try to refresh with old tokens - should fail
        refresh_url = "/api/v1/accounts/auth/token/refresh/"

        # Test first old token
        response1 = self.client.post(refresh_url, {"refresh": str(old_refresh1)}, format="json")
        self.assertEqual(
            response1.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Old refresh token should be invalid after password change",
        )

        # Test second old token
        response2 = self.client.post(refresh_url, {"refresh": str(old_refresh2)}, format="json")
        self.assertEqual(
            response2.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Old refresh token should be invalid after password change",
        )

        # Verify we can create new tokens with new password
        login_url = "/api/v1/accounts/auth/token/"
        login_response = self.client.post(
            login_url,
            {"username": self.user.username, "password": "NewSecurePassword123!"},
            format="json",
        )
        self.assertEqual(
            login_response.status_code,
            status.HTTP_200_OK,
            "Should be able to login with new password",
        )

    def test_password_change_clears_cookies(self):
        """Test that password change response clears authentication cookies."""
        self.authenticate_user()
        url = "/api/v1/accounts/auth/change-password/"
        data = {
            "old_password": "testpass123",
            "new_password": "NewSecurePassword123!",
            "new_password_confirm": "NewSecurePassword123!",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify both cookies are present in response (being cleared)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

        # Verify cookies are cleared (empty value or max_age=0)
        access_cookie = response.cookies["access_token"]
        refresh_cookie = response.cookies["refresh_token"]

        # Check cookies are being deleted
        self.assertTrue(
            access_cookie.value == "" or access_cookie["max-age"] == 0,
            "Access token cookie should be cleared",
        )
        self.assertTrue(
            refresh_cookie.value == "" or refresh_cookie["max-age"] == 0,
            "Refresh token cookie should be cleared",
        )


class PasswordChangeRateLimitTest(TestCase):
    """Separate test class for rate limiting to avoid interference."""

    databases = ["default", "accounts"]

    def setUp(self):
        """Set up test data with unique user for rate limit testing."""
        self.client = APIClient()
        self.user = User.objects.db_manager("accounts").create_user(
            username="ratelimituser", email="ratelimit@example.com", password="testpass123"
        )
        # Create basic profile setup
        self.organization = baker.make(Organization, name="Rate Limit Org", _using="accounts")
        self.tier = baker.make(Tier, tier_name="Tier 2", level=2, _using="accounts")

        try:
            self.profile = self.user.profile
            self.profile.organization = self.organization
            self.profile.tier = self.tier
            self.profile.save(using="accounts")
        except Profile.DoesNotExist:
            self.profile = baker.make(
                Profile,
                user=self.user,
                organization=self.organization,
                tier=self.tier,
                _using="accounts",
            )

    def authenticate_user(self):
        """Authenticate the test user."""
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        return refresh.access_token, refresh

    def test_password_change_rate_limit_exceeded(self):
        """Test rate limiting on password change endpoint."""
        # Skip if rate limiting is disabled (e.g., in test environment)
        if not getattr(settings, "RATELIMIT_ENABLE", True):
            self.skipTest("Rate limiting is disabled in test environment")

        self.authenticate_user()
        url = "/api/v1/accounts/auth/change-password/"

        # Make multiple requests to trigger rate limit (5 per minute)
        for i in range(6):
            data = {
                "old_password": "testpass123",
                "new_password": f"NewPassword{i}!",
                "new_password_confirm": f"NewPassword{i}!",
            }
            response = self.client.post(url, data, format="json")

            if i < 5:
                # First 5 should either succeed, fail validation, or be rate limited
                self.assertIn(
                    response.status_code,
                    [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN],
                )
                if response.status_code == status.HTTP_403_FORBIDDEN:
                    # Rate limit triggered
                    break
            else:
                # 6th request should be rate limited
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                break
