from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured


class SharedConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shared"

    def ready(self):
        """
        Perform startup validation when Django initializes.
        This ensures critical configuration is present before the app runs.
        """
        self.validate_rate_limits()

    def validate_rate_limits(self):
        """
        Validate that all required rate limit keys are configured.

        Raises:
            ImproperlyConfigured: If any required rate limit key is missing
        """
        from django.conf import settings

        # Required rate limit keys that must be present
        required_keys = [
            "LOGIN",
            "REGISTRATION",
            "PASSWORD_CHANGE",
            "PASSWORD_RESET_REQUEST",
            "PASSWORD_RESET_CONFIRM",
            "EMAIL_VERIFICATION",
            "PROFILE_UPDATE",
            "USERNAME_UPDATE",
            "LOGOUT",
        ]

        # Check if RATE_LIMITS setting exists
        if not hasattr(settings, "RATE_LIMITS"):
            raise ImproperlyConfigured(
                "RATE_LIMITS setting is missing from settings.py. "
                "Please configure rate limiting for production deployment."
            )

        rate_limits = settings.RATE_LIMITS
        missing_keys = [key for key in required_keys if key not in rate_limits]

        if missing_keys:
            raise ImproperlyConfigured(
                f"Missing required rate limit configuration keys: {', '.join(missing_keys)}\n"
                f"Please add these keys to the RATE_LIMITS dictionary in settings.py.\n"
                f"Example:\n"
                f"RATE_LIMITS = {{\n"
                f"    'PASSWORD_RESET_REQUEST': config('RATE_LIMIT_PASSWORD_RESET_REQUEST', default='3/m'),\n"
                f"    # ... other keys\n"
                f"}}"
            )
