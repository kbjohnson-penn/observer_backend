from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from django.contrib.auth import get_user_model
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from shared.api.error_handlers import handle_validation_error

User = get_user_model()

from accounts.api.serializers.auth_serializers import CustomTokenObtainPairSerializer


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT login view to update last login timestamp.
    Rate limited to 5 attempts per minute per IP.
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        # Only update last_login if authentication was successful
        if response.status_code == status.HTTP_200_OK:
            try:
                username = request.data.get('username')
                if username:
                    user = User.objects.using('accounts').get(username=username)
                    user.last_login = timezone.now()
                    user.save(using='accounts')
            except User.DoesNotExist:
                # Don't reveal user existence in login endpoint
                pass
            except Exception as e:
                # Log error but don't fail the response
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to update last_login for user: {e}")
        
        return response


class LogoutView(APIView):
    """
    Logout view to blacklist the refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return handle_validation_error(
                detail="Refresh token is required.",
                errors={"refresh": ["This field is required."]}
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return handle_validation_error(
                detail="Invalid refresh token.",
                log_message=f"Token blacklist failed: {str(e)}"
            )
