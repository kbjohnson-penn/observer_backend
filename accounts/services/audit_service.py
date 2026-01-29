"""
Audit Service for centralized audit trail logging.

Provides a clean interface for logging user actions to the AuditTrail model.
All audit logging should go through this service to ensure consistency.
"""

import ipaddress
import logging
from typing import TYPE_CHECKING, Optional

from accounts.models import AuditTrail

if TYPE_CHECKING:
    from accounts.models import FailedLoginAttempt

logger = logging.getLogger(__name__)


class AuditService:
    """
    Service for logging audit trail events.

    Usage:
        from accounts.services import AuditService

        # Log a successful action
        AuditService.log(
            request=request,
            event_type=AuditEventTypes.AUTH_LOGIN_SUCCESS,
            category=AuditCategories.AUTHENTICATION,
            description="User logged in successfully",
            metadata={"method": "password"}
        )

        # Log a failed login (no user object)
        AuditService.log_failed_login(
            request=request,
            attempted_username="user@example.com",
            failure_reason="Invalid password"
        )

    Note:
        All logging methods fail silently (return None) on errors to avoid
        disrupting the main request flow. Errors are logged for monitoring.
    """

    @staticmethod
    def _validate_ip(ip_str: Optional[str]) -> Optional[str]:
        """
        Validate IP address format.

        Args:
            ip_str: IP address string to validate

        Returns:
            Validated IP address or None if invalid
        """
        if not ip_str:
            return None
        try:
            ip_str = ip_str.strip()
            ipaddress.ip_address(ip_str)
            return ip_str
        except ValueError:
            # Truncate to prevent log injection from malicious X-Forwarded-For headers
            logger.warning("Invalid IP address format: %s", ip_str[:50] if ip_str else "")
            return None

    @staticmethod
    def get_client_ip(request) -> Optional[str]:
        """
        Extract and validate client IP address from request, handling proxy headers.

        Args:
            request: Django/DRF request object

        Returns:
            Validated client IP address or None
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
            return AuditService._validate_ip(ip)
        return AuditService._validate_ip(request.META.get("REMOTE_ADDR"))

    @staticmethod
    def log(
        request,
        event_type: str,
        category: str,
        description: str,
        metadata: Optional[dict] = None,
        user=None,
    ) -> Optional[AuditTrail]:
        """
        Create an audit trail entry.

        Args:
            request: Django/DRF request object
            event_type: Specific event type (e.g., AUTH_LOGIN_SUCCESS)
            category: High-level category (e.g., AUTHENTICATION)
            description: Human-readable description
            metadata: Optional dict with event-specific data
            user: Optional user override (defaults to request.user)

        Returns:
            Created AuditTrail instance, or None if logging failed
        """
        audit_user = user if user is not None else request.user

        # Store user info in metadata for historical reference (in case user is deleted)
        audit_metadata = metadata.copy() if metadata else {}
        if audit_user and hasattr(audit_user, "id"):
            audit_metadata["_user_id"] = audit_user.id
            # Sanitize username to prevent log injection
            raw_username = getattr(audit_user, "username", None) or ""
            audit_metadata["_username"] = AuditService._sanitize_string(raw_username)

        # Extract user identifier for HIPAA compliance (preserved if user is deleted)
        user_identifier = ""
        if audit_user and hasattr(audit_user, "email"):
            user_identifier = AuditService._sanitize_string(
                getattr(audit_user, "email", ""), max_length=255
            )

        try:
            return AuditTrail.objects.using("accounts").create(
                user=audit_user,
                user_identifier=user_identifier,
                event_type=event_type,
                category=category,
                description=description,
                metadata=audit_metadata,
                ip_address=AuditService.get_client_ip(request),
                user_agent=AuditService._sanitize_user_agent(
                    request.META.get("HTTP_USER_AGENT", "")
                ),
            )
        except Exception as e:
            # Log error but don't crash the request - audit failures shouldn't block operations
            logger.error(f"Failed to create audit trail entry: {e}", exc_info=True)
            return None

    @staticmethod
    def _sanitize_string(value: str, max_length: int = 100) -> str:
        """
        Sanitize string input to prevent log injection attacks.

        Args:
            value: Raw string input
            max_length: Maximum allowed length

        Returns:
            Sanitized string
        """
        if not value:
            return ""
        # Truncate to max length and remove non-printable characters
        sanitized = value[:max_length]
        sanitized = "".join(c for c in sanitized if c.isprintable())
        return sanitized

    @staticmethod
    def _sanitize_user_agent(user_agent: str, max_length: int = 500) -> str:
        """
        Sanitize user agent string to prevent log injection attacks.

        Args:
            user_agent: Raw user agent string
            max_length: Maximum allowed length

        Returns:
            Sanitized user agent string
        """
        return AuditService._sanitize_string(user_agent, max_length)

    @staticmethod
    def log_failed_login(
        request,
        attempted_username: str,
        failure_reason: str,
    ) -> Optional["FailedLoginAttempt"]:
        """
        Log a failed login attempt.

        Uses FailedLoginAttempt model since failed logins don't have
        a valid user object to reference.

        Args:
            request: Django/DRF request object
            attempted_username: Username/email that was attempted
            failure_reason: Why the login failed

        Returns:
            Created FailedLoginAttempt instance, or None if logging failed
        """
        from accounts.models import FailedLoginAttempt

        # Sanitize username to prevent log injection
        safe_username = AuditService._sanitize_string(attempted_username)

        try:
            return FailedLoginAttempt.objects.using("accounts").create(
                attempted_username=safe_username,
                failure_reason=failure_reason,
                ip_address=AuditService.get_client_ip(request),
                user_agent=AuditService._sanitize_user_agent(
                    request.META.get("HTTP_USER_AGENT", "")
                ),
            )
        except Exception as e:
            # Log error but don't crash the request - audit failures shouldn't block operations
            logger.error(f"Failed to log failed login attempt: {e}", exc_info=True)
            return None
