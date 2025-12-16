import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.db import transaction
from django.middleware.csrf import get_token
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from django_ratelimit.decorators import ratelimit
from rest_framework import serializers, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from accounts.api.serializers.auth_serializers import (
    CustomTokenObtainPairSerializer,
    EmailVerificationSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserRegistrationSerializer,
)
from accounts.models.user_models import EmailVerificationToken, PasswordResetToken
from accounts.services import AuditService
from accounts.services.audit_constants import AuditCategories, AuditEventTypes
from shared.api.error_handlers import handle_server_error, handle_validation_error

User = get_user_model()
logger = logging.getLogger(__name__)


def get_cookie_settings():
    """
    Get consistent cookie settings for JWT tokens.
    Returns a dict with domain, httponly, secure, and samesite settings.
    """
    return {
        "domain": getattr(settings, "SESSION_COOKIE_DOMAIN", None),
        "httponly": True,
        "secure": not settings.DEBUG,
        "samesite": "None" if not settings.DEBUG else "Lax",
    }


def set_auth_cookie(response, name, value, max_age):
    """Set an authentication cookie with consistent settings."""
    cookie_settings = get_cookie_settings()
    response.set_cookie(
        name,
        value,
        max_age=max_age,
        path="/",  # Explicitly set root path to match delete_auth_cookie
        **cookie_settings,
    )


def delete_auth_cookie(response, name):
    """Delete an authentication cookie with consistent settings."""
    cookie_settings = get_cookie_settings()
    response.delete_cookie(
        name,
        domain=cookie_settings["domain"],
        path="/",  # Must match path used when setting cookies
        samesite=cookie_settings["samesite"],
    )


@method_decorator(
    ratelimit(key="ip", rate=settings.RATE_LIMITS["LOGIN"], method="POST", block=True), name="post"
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT login view to update last login timestamp and set httpOnly cookies.
    Rate limiting configured via settings.RATE_LIMITS['LOGIN'].
    CSRF protection enabled - frontend must include CSRF token.
    """

    serializer_class = CustomTokenObtainPairSerializer

    def _get_user_by_username(self, username: str):
        """Fetch user by username or email."""
        if "@" in username:
            return User.objects.using("accounts").get(email=username)
        return User.objects.using("accounts").get(username=username)

    def _set_token_cookies(self, response, access_token, refresh_token):
        """Set httpOnly cookies for JWT tokens."""
        if access_token:
            set_auth_cookie(
                response,
                "access_token",
                access_token,
                max_age=settings.SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME").total_seconds(),
            )
        if refresh_token:
            set_auth_cookie(
                response,
                "refresh_token",
                refresh_token,
                max_age=settings.SIMPLE_JWT.get("REFRESH_TOKEN_LIFETIME").total_seconds(),
            )

    def _handle_successful_login(self, request, response, username: str):
        """Process successful login: update user, log audit, set cookies."""
        if not username:
            return

        try:
            user = self._get_user_by_username(username)
            user.last_login = timezone.now()
            user.save(using="accounts")

            AuditService.log(
                request=request,
                event_type=AuditEventTypes.AUTH_LOGIN_SUCCESS,
                category=AuditCategories.AUTHENTICATION,
                description="User logged in successfully",
                metadata={"login_method": "email" if "@" in username else "username"},
                user=user,
            )

            self._set_token_cookies(
                response, response.data.get("access"), response.data.get("refresh")
            )

            # Build secure response (remove tokens from body)
            access_lifetime = settings.SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME")
            expires_at = int((timezone.now() + access_lifetime).timestamp())
            response.data = {
                "detail": "Login successful",
                "user": {"username": user.username, "email": user.email, "id": user.id},
                "expires_at": expires_at,
            }
        except User.DoesNotExist:
            logger.warning(
                "Authentication succeeded but user lookup failed for username: %s", username
            )
        except Exception as e:
            logger.error("Failed to update last_login for user: %s", e)

    def post(self, request, *args, **kwargs):
        username = request.data.get("username", "")

        try:
            response = super().post(request, *args, **kwargs)
        except (InvalidToken, TokenError, AuthenticationFailed):
            # Only log failed login for authentication-related exceptions
            # Other exceptions (DB errors, etc.) should propagate without being logged as auth failures
            AuditService.log_failed_login(
                request=request,
                attempted_username=username,
                failure_reason="invalid_credentials",
            )
            raise

        if response.status_code == status.HTTP_200_OK:
            self._handle_successful_login(request, response, username)

        return response


class LogoutView(APIView):
    """
    Logout view to blacklist the refresh token and clear httpOnly cookies.
    CSRF protection enabled.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Log logout before clearing cookies
        AuditService.log(
            request=request,
            event_type=AuditEventTypes.AUTH_LOGOUT,
            category=AuditCategories.AUTHENTICATION,
            description="User logged out",
            metadata={},
        )

        # Get refresh token from cookie
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            # Fallback to request body for backward compatibility
            refresh_token = request.data.get("refresh")

        response = Response({"detail": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)

        # Clear httpOnly cookies with consistent settings
        delete_auth_cookie(response, "access_token")
        delete_auth_cookie(response, "refresh_token")

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                # Still log the error but don't fail logout
                logger.error("Token blacklist failed: %s", str(e))

        return response


@method_decorator(
    ratelimit(
        key="user_or_ip", rate=settings.RATE_LIMITS["TOKEN_REFRESH"], method="POST", block=True
    ),
    name="post",
)
class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom JWT refresh view that works with httpOnly cookies.
    Rate limiting configured via settings.RATE_LIMITS['TOKEN_REFRESH'].
    CSRF protection enabled.
    """

    def post(self, request, *args, **kwargs):
        # Get refresh token from cookie
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found in cookies"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Add refresh token to request data
        request.data["refresh"] = refresh_token

        # Call parent method
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            # Set new access token in httpOnly cookie
            access_token = response.data.get("access")
            new_refresh_token = response.data.get("refresh")

            if access_token:
                set_auth_cookie(
                    response,
                    "access_token",
                    access_token,
                    max_age=settings.SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME").total_seconds(),
                )

            if new_refresh_token:
                set_auth_cookie(
                    response,
                    "refresh_token",
                    new_refresh_token,
                    max_age=settings.SIMPLE_JWT.get("REFRESH_TOKEN_LIFETIME").total_seconds(),
                )

            # Remove tokens from response body
            # Include access token expiry for frontend auto-logout scheduling
            access_lifetime = settings.SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME")
            expires_at = int((timezone.now() + access_lifetime).timestamp())
            response.data = {"detail": "Token refresh successful", "expires_at": expires_at}

            # Log token refresh - get user from refresh token since access token may be expired
            try:
                token = RefreshToken(refresh_token)
                user_id = token.payload.get("user_id")
                user = User.objects.using("accounts").get(id=user_id)
                AuditService.log(
                    request=request,
                    user=user,
                    event_type=AuditEventTypes.AUTH_TOKEN_REFRESH,
                    category=AuditCategories.AUTHENTICATION,
                    description="Token refreshed",
                    metadata={},
                )
            except Exception as e:
                # Token decode or user lookup failed, skip audit logging
                logger.warning(f"Failed to log token refresh audit: {e}")

        return response


@method_decorator(
    ratelimit(key="ip", rate=settings.RATE_LIMITS["TOKEN_VERIFY"], method="POST", block=True),
    name="post",
)
class CustomTokenVerifyView(TokenVerifyView):
    """
    Custom JWT verify view that reads access token from httpOnly cookies.
    Rate limiting configured via settings.RATE_LIMITS['TOKEN_VERIFY'].
    """

    def post(self, request, *args, **kwargs):
        # Get access token from cookie
        access_token = request.COOKIES.get("access_token")

        if not access_token:
            return Response(
                {"detail": "Access token not found in cookies"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Add token to request data for parent class
        request.data["token"] = access_token

        # Call parent method
        return super().post(request, *args, **kwargs)


@method_decorator(
    ratelimit(key="ip", rate=settings.RATE_LIMITS["REGISTRATION"], method="POST", block=True),
    name="post",
)
class UserRegistrationView(APIView):
    """
    User registration view. Creates inactive user and sends verification email.
    Rate limiting configured via settings.RATE_LIMITS['REGISTRATION'].
    CSRF protection enabled.
    """

    permission_classes = []  # Allow anonymous access

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.save()

                # Create verification token
                verification_token = EmailVerificationToken.objects.db_manager("accounts").create(
                    user=user
                )

                # Send verification email (non-blocking - registration succeeds even if email fails)
                self.send_verification_email(user, verification_token.token)

                # Log successful registration
                AuditService.log(
                    request=request,
                    event_type=AuditEventTypes.AUTH_REGISTRATION,
                    category=AuditCategories.AUTHENTICATION,
                    description="New user registered",
                    metadata={},
                    user=user,
                )

                return Response(
                    {
                        "detail": "Registration successful. Please check your email to verify your account.",
                        "email": user.email,
                    },
                    status=status.HTTP_201_CREATED,
                )

            except serializers.ValidationError:
                # Re-raise validation errors to be handled by DRF
                raise
            except Exception as e:
                # Log unexpected errors with full traceback
                logger.error("Unexpected registration error: %s", str(e), exc_info=True)

                return handle_server_error(
                    detail="Registration failed due to a server error. Please try again later.",
                    log_message=f"Registration error: {str(e)}",
                    exception=e,
                )

        return handle_validation_error(
            detail="Registration failed due to invalid data.", errors=serializer.errors
        )

    def send_verification_email(self, user, token):
        """Send verification email to user - non-blocking"""
        try:
            # Get frontend URL from settings or environment
            frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")
            verification_url = f"{frontend_url}/verify-email?token={token}"

            logger.info("Attempting to send verification email to %s", user.email)
            logger.debug(
                "Email configuration: HOST=%s, PORT=%s, USER=%s",
                getattr(settings, "EMAIL_HOST", "Not configured"),
                getattr(settings, "EMAIL_PORT", "Not configured"),
                getattr(settings, "EMAIL_HOST_USER", "Not configured"),
            )

            subject = "Verify your Observer account"
            message = f"""
Hello {user.first_name},

Thank you for registering with Observer. Please click the link below to verify your email address and set up your password:

{verification_url}

This link will expire in 24 hours.

If you didn't create an account, please ignore this email.

Best regards,
The Observer Team
            """.strip()

            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@observer.com"),
                recipient_list=[user.email],
                fail_silently=True,  # Don't crash registration if email fails
            )

            logger.info("Verification email sent successfully to %s", user.email)

        except Exception as e:
            # Log error with full traceback for debugging
            logger.error(
                "Failed to send verification email to %s: %s", user.email, str(e), exc_info=True
            )


@method_decorator(
    ratelimit(key="ip", rate=settings.RATE_LIMITS["EMAIL_VERIFICATION"], method="POST", block=True),
    name="post",
)
class EmailVerificationView(APIView):
    """
    Email verification view. Verifies token and allows password setup.
    Rate limiting configured via settings.RATE_LIMITS['EMAIL_VERIFICATION'].
    CSRF protection enabled.
    """

    permission_classes = []  # Allow anonymous access

    def post(self, request, *args, **kwargs):
        serializer = EmailVerificationSerializer(data=request.data)

        if serializer.is_valid():
            token = serializer.validated_data["token"]
            password = serializer.validated_data["password"]

            try:
                # Find verification token
                verification_token = EmailVerificationToken.objects.using("accounts").get(
                    token=token
                )

                # Check if token is valid
                if not verification_token.is_valid():
                    return handle_validation_error(detail="Invalid or expired verification token.")

                # Activate user and set password
                user = verification_token.user
                user.is_active = True
                user.email_verified = True
                user.set_password(password)
                user.save(using="accounts")

                # Mark token as used
                verification_token.is_used = True
                verification_token.save(using="accounts")

                # Log email verification
                AuditService.log(
                    request=request,
                    event_type=AuditEventTypes.AUTH_EMAIL_VERIFIED,
                    category=AuditCategories.AUTHENTICATION,
                    description="Email verified",
                    metadata={},
                    user=user,
                )

                return Response(
                    {
                        "detail": "Email verified successfully. You can now log in.",
                        "email": user.email,
                    },
                    status=status.HTTP_200_OK,
                )

            except EmailVerificationToken.DoesNotExist:
                return handle_validation_error(detail="Invalid verification token.")
            except Exception as e:
                return handle_validation_error(
                    detail="Email verification failed. Please try again.",
                    log_message=f"Email verification error: {str(e)}",
                )

        return handle_validation_error(
            detail="Email verification failed due to invalid data.", errors=serializer.errors
        )


class CSRFTokenView(APIView):
    """
    Endpoint to get CSRF token for frontend forms.
    This ensures the frontend can get a CSRF token for state-changing operations.
    """

    permission_classes = []  # Allow unauthenticated access

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        """Return CSRF token"""
        token = get_token(request)
        return Response({"csrfToken": token, "detail": "CSRF token generated successfully"})


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password_confirm = serializers.CharField(required=True)

    def validate_new_password(self, value):
        """Validate new password using Django's password validators."""
        user = self.context.get("request").user if self.context.get("request") else None
        validate_password(value, user=user)
        return value

    def validate(self, data):
        """Validate that new passwords match"""
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": ["New passwords do not match."]}
            )
        return data


@method_decorator(
    ratelimit(key="user", rate=settings.RATE_LIMITS["PASSWORD_CHANGE"], method="POST", block=True),
    name="post",
)
class PasswordChangeView(APIView):
    """
    Change user password. Requires old password for verification.
    Blacklists all existing refresh tokens and logs user out for security.
    Rate limiting configured via settings.RATE_LIMITS['PASSWORD_CHANGE'].
    CSRF protection enabled.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = PasswordChangeSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            old_password = serializer.validated_data["old_password"]
            new_password = serializer.validated_data["new_password"]

            user = request.user

            # Verify old password
            if not user.check_password(old_password):
                return Response(
                    {"old_password": ["Current password is incorrect."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Set new password
            user.set_password(new_password)
            user.save(using="accounts")

            # Log password change
            AuditService.log(
                request=request,
                event_type=AuditEventTypes.AUTH_PASSWORD_CHANGED,
                category=AuditCategories.AUTHENTICATION,
                description="Password changed",
                metadata={},
            )

            # Blacklist all outstanding tokens for this user for security
            try:
                outstanding_tokens = OutstandingToken.objects.using("accounts").filter(user=user)
                for outstanding_token in outstanding_tokens:
                    try:
                        token = RefreshToken(outstanding_token.token)
                        token.blacklist()
                    except Exception as e:
                        # Token might already be blacklisted or invalid
                        logger.warning(
                            f"Could not blacklist token {outstanding_token.id} for user {user.id}: {e}"
                        )
            except Exception as e:
                logger.error(
                    f"Error blacklisting tokens for user {user.id} after password change: {e}"
                )

            # Create response with logout required flag
            response = Response(
                {
                    "detail": "Password updated successfully. Please log in again with your new password.",
                    "logout_required": True,
                },
                status=status.HTTP_200_OK,
            )

            # Clear httpOnly cookies to force logout with consistent settings
            delete_auth_cookie(response, "access_token")
            delete_auth_cookie(response, "refresh_token")

            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(
    ratelimit(
        key="ip", rate=settings.RATE_LIMITS["PASSWORD_RESET_REQUEST"], method="POST", block=True
    ),
    name="post",
)
class PasswordResetRequestView(APIView):
    """
    Request password reset. Sends email with reset link if user exists.
    Always returns same response to prevent user enumeration.
    Rate limiting configured via settings.RATE_LIMITS['PASSWORD_RESET_REQUEST'].
    """

    permission_classes = []  # Allow anonymous access

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]

            try:
                user = User.objects.using("accounts").get(email=email, is_active=True)

                # Invalidate any existing unused tokens for this user
                PasswordResetToken.objects.using("accounts").filter(
                    user=user, is_used=False
                ).update(is_used=True)

                # Create new token
                reset_token = PasswordResetToken.objects.db_manager("accounts").create(user=user)

                # Send email (non-blocking)
                self.send_password_reset_email(user, reset_token.token)

                # Log password reset request (no PII in metadata - user object provides context)
                AuditService.log(
                    request=request,
                    event_type=AuditEventTypes.AUTH_PASSWORD_RESET_REQUEST,
                    category=AuditCategories.AUTHENTICATION,
                    description="Password reset requested",
                    metadata={},
                    user=user,
                )
            except User.DoesNotExist:
                # Don't reveal if email exists - log for monitoring
                logger.info("Password reset requested for non-existent email: %s", email)

            # Always return success to prevent user enumeration
            return Response(
                {
                    "detail": "If an account exists with this email, you will receive a password reset link."
                },
                status=status.HTTP_200_OK,
            )

        return handle_validation_error(
            detail="Invalid request.",
            errors=serializer.errors,
        )

    def send_password_reset_email(self, user, token):
        """Send password reset email - non-blocking"""
        try:
            frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")
            reset_url = f"{frontend_url}/reset-password?token={token}"

            subject = "Reset your Observer password"
            message = f"""
Hello {user.first_name},

You requested to reset your password for your Observer account. Click the link below to set a new password:

{reset_url}

This link will expire in 1 hour.

If you didn't request a password reset, please ignore this email. Your password will remain unchanged.

Best regards,
The Observer Team
            """.strip()

            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@observer.com"),
                recipient_list=[user.email],
                fail_silently=True,
            )

            logger.info("Password reset email sent to %s", user.email)
        except Exception as e:
            logger.error(
                "Failed to send password reset email to %s: %s", user.email, str(e), exc_info=True
            )


@method_decorator(
    ratelimit(
        key="ip", rate=settings.RATE_LIMITS["PASSWORD_RESET_CONFIRM"], method="POST", block=True
    ),
    name="post",
)
class PasswordResetConfirmView(APIView):
    """
    Confirm password reset with token and new password.
    Invalidates all existing sessions after successful reset.
    Rate limiting configured via settings.RATE_LIMITS['PASSWORD_RESET_CONFIRM'].
    """

    permission_classes = []  # Allow anonymous access

    def _blacklist_user_tokens(self, user):
        """Blacklist all outstanding refresh tokens for a user."""
        try:
            outstanding_tokens = OutstandingToken.objects.using("accounts").filter(user=user)
            for outstanding_token in outstanding_tokens:
                try:
                    refresh = RefreshToken(outstanding_token.token)
                    refresh.blacklist()
                except Exception as e:
                    logger.warning(f"Could not blacklist token for user {user.id}: {e}")
        except Exception as e:
            logger.error(f"Error blacklisting tokens after password reset: {e}")

    def _reset_password(self, token, password):
        """
        Reset user password atomically.
        Returns the user on success, raises exception on failure.
        """
        with transaction.atomic(using="accounts"):
            reset_token = (
                PasswordResetToken.objects.using("accounts").select_for_update().get(token=token)
            )

            if not reset_token.is_valid():
                return None

            user = reset_token.user
            user.set_password(password)
            user.save(using="accounts")

            reset_token.is_used = True
            reset_token.save(using="accounts")

            return user

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)

        if not serializer.is_valid():
            return handle_validation_error(detail="Invalid request.", errors=serializer.errors)

        token = serializer.validated_data["token"]
        password = serializer.validated_data["password"]

        try:
            user = self._reset_password(token, password)

            if user is None:
                return handle_validation_error(
                    detail="This password reset link has expired or already been used. Please request a new one."
                )

            self._blacklist_user_tokens(user)

            AuditService.log(
                request=request,
                event_type=AuditEventTypes.AUTH_PASSWORD_RESET_COMPLETE,
                category=AuditCategories.AUTHENTICATION,
                description="Password reset completed",
                metadata={},
                user=user,
            )

            return Response(
                {
                    "detail": "Your password has been reset successfully. You can now log in with your new password."
                },
                status=status.HTTP_200_OK,
            )

        except PasswordResetToken.DoesNotExist:
            return handle_validation_error(
                detail="Invalid password reset link. Please request a new one."
            )
        except Exception as e:
            logger.error("Password reset error: %s", str(e), exc_info=True)
            return handle_server_error(
                detail="Password reset failed. Please try again later.",
                log_message=f"Password reset error: {str(e)}",
                exception=e,
            )
