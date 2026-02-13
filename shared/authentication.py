from django.contrib.auth import get_user_model

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError

User = get_user_model()


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that extracts tokens from httpOnly cookies
    instead of Authorization headers.
    """

    def authenticate(self, request):
        # Try to get token from cookie first
        raw_token = request.COOKIES.get("access_token")

        if raw_token is None:
            # Fallback to Authorization header for backward compatibility
            header = self.get_header(request)
            if header is None:
                return None
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except TokenError:
            return None
