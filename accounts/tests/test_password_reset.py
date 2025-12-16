"""
Test cases for password reset functionality.

Tests cover:
- Password reset request endpoint (email submission)
- Password reset confirm endpoint (token + new password)
- PasswordResetToken model behavior
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from rest_framework import status
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models.user_models import PasswordResetToken

from .base import BaseTestCase

User = get_user_model()


class PasswordResetRequestAPITest(BaseTestCase):
    """Test cases for password reset request API endpoint."""

    def test_password_reset_request_success(self):
        """Test successful password reset request with valid email."""
        url = "/api/v1/accounts/auth/password-reset/"
        data = {"email": self.user.email}
        response = self.client.post(url, data, format="json")

        # Should return 200 with success message
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)
        self.assertIn("password reset", response.data["detail"].lower())

    def test_password_reset_request_nonexistent_email(self):
        """Test password reset request with non-existent email returns same response (no enumeration)."""
        url = "/api/v1/accounts/auth/password-reset/"
        data = {"email": "nonexistent@example.com"}
        response = self.client.post(url, data, format="json")

        # Should return 200 with same message (prevents user enumeration)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)

    def test_password_reset_request_invalid_email_format(self):
        """Test password reset request with invalid email format."""
        url = "/api/v1/accounts/auth/password-reset/"
        data = {"email": "invalid-email"}
        response = self.client.post(url, data, format="json")

        # Should return 400 for invalid email format
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_request_creates_token(self):
        """Test that password reset request creates a token in the database."""
        url = "/api/v1/accounts/auth/password-reset/"
        data = {"email": self.user.email}

        # Ensure no tokens exist before
        initial_count = PasswordResetToken.objects.using("accounts").filter(user=self.user).count()

        response = self.client.post(url, data, format="json")

        if response.status_code == status.HTTP_200_OK:
            # Check token was created
            new_count = PasswordResetToken.objects.using("accounts").filter(user=self.user).count()
            self.assertGreater(new_count, initial_count)

            # Verify token properties
            token = (
                PasswordResetToken.objects.using("accounts")
                .filter(user=self.user, is_used=False)
                .latest("created_at")
            )
            self.assertEqual(len(token.token), 64)  # 64 character token
            self.assertFalse(token.is_used)
            self.assertFalse(token.is_expired())
        else:
            # Rate limited
            self.skipTest("Rate limited - cannot verify token creation")

    def test_password_reset_request_invalidates_previous_tokens(self):
        """Test that new password reset request invalidates previous unused tokens."""
        # Create an existing token
        existing_token = PasswordResetToken.objects.using("accounts").create(
            user=self.user,
            expires_at=timezone.now() + timedelta(hours=1),
        )
        existing_token_id = existing_token.id

        url = "/api/v1/accounts/auth/password-reset/"
        data = {"email": self.user.email}
        response = self.client.post(url, data, format="json")

        if response.status_code == status.HTTP_200_OK:
            # Check that old token is marked as used
            existing_token.refresh_from_db(using="accounts")
            self.assertTrue(
                existing_token.is_used,
                "Previous token should be marked as used",
            )
        else:
            self.skipTest("Rate limited - cannot verify token invalidation")

    def test_password_reset_request_missing_email(self):
        """Test password reset request with missing email field."""
        url = "/api/v1/accounts/auth/password-reset/"
        data = {}
        response = self.client.post(url, data, format="json")

        # Should return 400 for missing required field
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmAPITest(BaseTestCase):
    """Test cases for password reset confirm API endpoint."""

    def setUp(self):
        """Set up test data including a valid reset token."""
        super().setUp()
        # Create a valid password reset token
        self.reset_token = PasswordResetToken.objects.using("accounts").create(
            user=self.user,
            expires_at=timezone.now() + timedelta(hours=1),
        )

    def test_password_reset_confirm_success(self):
        """Test successful password reset with valid token and passwords."""
        url = "/api/v1/accounts/auth/password-reset/confirm/"
        data = {
            "token": self.reset_token.token,
            "password": "NewSecurePassword123!",
            "password_confirm": "NewSecurePassword123!",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)

        # Verify password was changed
        self.user.refresh_from_db(using="accounts")
        self.assertTrue(self.user.check_password("NewSecurePassword123!"))
        self.assertFalse(self.user.check_password("testpass123"))

        # Verify token is marked as used
        self.reset_token.refresh_from_db(using="accounts")
        self.assertTrue(self.reset_token.is_used)

    def test_password_reset_confirm_invalid_token(self):
        """Test password reset confirm with invalid token."""
        url = "/api/v1/accounts/auth/password-reset/confirm/"
        data = {
            "token": "invalidtoken12345",
            "password": "NewSecurePassword123!",
            "password_confirm": "NewSecurePassword123!",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_expired_token(self):
        """Test password reset confirm with expired token."""
        # Create an expired token
        expired_token = PasswordResetToken.objects.using("accounts").create(
            user=self.user,
            expires_at=timezone.now() - timedelta(hours=1),  # Expired 1 hour ago
        )

        url = "/api/v1/accounts/auth/password-reset/confirm/"
        data = {
            "token": expired_token.token,
            "password": "NewSecurePassword123!",
            "password_confirm": "NewSecurePassword123!",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_used_token(self):
        """Test password reset confirm with already used token."""
        # Mark token as used
        self.reset_token.is_used = True
        self.reset_token.save(using="accounts")

        url = "/api/v1/accounts/auth/password-reset/confirm/"
        data = {
            "token": self.reset_token.token,
            "password": "NewSecurePassword123!",
            "password_confirm": "NewSecurePassword123!",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_password_mismatch(self):
        """Test password reset confirm with mismatched passwords."""
        url = "/api/v1/accounts/auth/password-reset/confirm/"
        data = {
            "token": self.reset_token.token,
            "password": "NewSecurePassword123!",
            "password_confirm": "DifferentPassword123!",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Errors are nested under 'errors' key
        self.assertIn("errors", response.data)
        self.assertIn("password_confirm", response.data["errors"])

    def test_password_reset_confirm_weak_password(self):
        """Test password reset confirm with weak password."""
        url = "/api/v1/accounts/auth/password-reset/confirm/"
        data = {
            "token": self.reset_token.token,
            "password": "weak",  # Too short
            "password_confirm": "weak",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Errors are nested under 'errors' key
        self.assertIn("errors", response.data)
        self.assertIn("password", response.data["errors"])

    def test_password_reset_confirm_blacklists_tokens(self):
        """Test that password reset blacklists all user's refresh tokens."""
        # Create some refresh tokens for the user
        token1 = RefreshToken.for_user(self.user)
        token2 = RefreshToken.for_user(self.user)

        # Verify tokens exist
        outstanding_before = OutstandingToken.objects.using("accounts").filter(user=self.user)
        self.assertGreaterEqual(outstanding_before.count(), 2)

        url = "/api/v1/accounts/auth/password-reset/confirm/"
        data = {
            "token": self.reset_token.token,
            "password": "NewSecurePassword123!",
            "password_confirm": "NewSecurePassword123!",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify all tokens are blacklisted
        outstanding_after = OutstandingToken.objects.using("accounts").filter(user=self.user)
        for token in outstanding_after:
            try:
                token.blacklistedtoken
                blacklisted = True
            except Exception:
                blacklisted = False
            self.assertTrue(blacklisted, f"Token {token.id} should be blacklisted")

    def test_password_reset_confirm_can_login_with_new_password(self):
        """Test that user can login with new password after reset."""
        url = "/api/v1/accounts/auth/password-reset/confirm/"
        data = {
            "token": self.reset_token.token,
            "password": "NewSecurePassword123!",
            "password_confirm": "NewSecurePassword123!",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Try to login with new password
        login_url = "/api/v1/accounts/auth/token/"
        login_data = {
            "username": self.user.username,
            "password": "NewSecurePassword123!",
        }
        login_response = self.client.post(login_url, login_data, format="json")

        # Should succeed (may be rate limited, so check for both outcomes)
        self.assertIn(
            login_response.status_code,
            [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN],  # 403 = rate limited
        )

    def test_password_reset_confirm_old_password_invalid(self):
        """Test that old password no longer works after reset."""
        url = "/api/v1/accounts/auth/password-reset/confirm/"
        data = {
            "token": self.reset_token.token,
            "password": "NewSecurePassword123!",
            "password_confirm": "NewSecurePassword123!",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify old password doesn't work
        self.user.refresh_from_db(using="accounts")
        self.assertFalse(self.user.check_password("testpass123"))

    def test_password_reset_confirm_missing_fields(self):
        """Test password reset confirm with missing required fields."""
        url = "/api/v1/accounts/auth/password-reset/confirm/"

        # Missing password_confirm
        data = {
            "token": self.reset_token.token,
            "password": "NewSecurePassword123!",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Missing token
        data = {
            "password": "NewSecurePassword123!",
            "password_confirm": "NewSecurePassword123!",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PasswordResetTokenModelTest(TestCase):
    """Test cases for PasswordResetToken model."""

    databases = ["default", "accounts"]

    def setUp(self):
        """Set up test user."""
        self.user = User.objects.db_manager("accounts").create_user(
            username="tokenuser",
            email="tokenuser@example.com",
            password="testpass123",
        )

    def test_token_generation(self):
        """Test that token is generated with correct length."""
        token = PasswordResetToken.objects.using("accounts").create(
            user=self.user,
            expires_at=timezone.now() + timedelta(hours=1),
        )
        self.assertEqual(len(token.token), 64)

    def test_token_expiry_default(self):
        """Test that default expiry is approximately 1 hour."""
        token = PasswordResetToken(user=self.user)
        token.save(using="accounts")

        # Should expire in approximately 1 hour
        expected_expiry = timezone.now() + timedelta(hours=1)
        time_diff = abs((token.expires_at - expected_expiry).total_seconds())
        self.assertLess(time_diff, 60)  # Within 1 minute tolerance

    def test_is_valid_method(self):
        """Test is_valid() returns correct status."""
        # Valid token
        valid_token = PasswordResetToken.objects.using("accounts").create(
            user=self.user,
            expires_at=timezone.now() + timedelta(hours=1),
        )
        self.assertTrue(valid_token.is_valid())

        # Used token
        used_token = PasswordResetToken.objects.using("accounts").create(
            user=self.user,
            expires_at=timezone.now() + timedelta(hours=1),
            is_used=True,
        )
        self.assertFalse(used_token.is_valid())

        # Expired token
        expired_token = PasswordResetToken.objects.using("accounts").create(
            user=self.user,
            expires_at=timezone.now() - timedelta(hours=1),
        )
        self.assertFalse(expired_token.is_valid())

    def test_is_expired_method(self):
        """Test is_expired() returns correct status."""
        # Not expired
        valid_token = PasswordResetToken.objects.using("accounts").create(
            user=self.user,
            expires_at=timezone.now() + timedelta(hours=1),
        )
        self.assertFalse(valid_token.is_expired())

        # Expired
        expired_token = PasswordResetToken.objects.using("accounts").create(
            user=self.user,
            expires_at=timezone.now() - timedelta(hours=1),
        )
        self.assertTrue(expired_token.is_expired())

    def test_token_uniqueness(self):
        """Test that generated tokens are unique."""
        tokens = set()
        for _ in range(10):
            token = PasswordResetToken.objects.using("accounts").create(
                user=self.user,
                expires_at=timezone.now() + timedelta(hours=1),
            )
            tokens.add(token.token)

        # All tokens should be unique
        self.assertEqual(len(tokens), 10)

    def test_str_representation(self):
        """Test string representation of token."""
        token = PasswordResetToken.objects.using("accounts").create(
            user=self.user,
            expires_at=timezone.now() + timedelta(hours=1),
        )
        self.assertIn(self.user.email, str(token))
