from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.utils import timezone
from django.contrib.auth import get_user_model
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.conf import settings
from shared.api.error_handlers import handle_validation_error

User = get_user_model()

from accounts.api.serializers.auth_serializers import (
    CustomTokenObtainPairSerializer, 
    UserRegistrationSerializer,
    EmailVerificationSerializer
)
from accounts.models.user_models import EmailVerificationToken


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT login view to update last login timestamp and set httpOnly cookies.
    Rate limited to 5 attempts per minute per IP.
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        # Only update last_login and set cookies if authentication was successful
        if response.status_code == status.HTTP_200_OK:
            try:
                username = request.data.get('username')
                if username:
                    # Handle email login - get username from email
                    if '@' in username:
                        user = User.objects.using('accounts').get(email=username)
                    else:
                        user = User.objects.using('accounts').get(username=username)
                    
                    user.last_login = timezone.now()
                    user.save(using='accounts')
                    
                    # Set httpOnly cookies for tokens
                    access_token = response.data.get('access')
                    refresh_token = response.data.get('refresh')
                    
                    if access_token:
                        response.set_cookie(
                            'access_token',
                            access_token,
                            max_age=settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME').total_seconds(),
                            httponly=True,
                            secure=not settings.DEBUG,  # Secure in production
                            samesite='Lax'
                        )
                    
                    if refresh_token:
                        response.set_cookie(
                            'refresh_token',
                            refresh_token,
                            max_age=settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME').total_seconds(),
                            httponly=True,
                            secure=not settings.DEBUG,  # Secure in production
                            samesite='Lax'
                        )
                    
                    # Remove tokens from response body for security
                    response.data = {
                        'detail': 'Login successful',
                        'user': {
                            'username': user.username,
                            'email': user.email,
                            'id': user.id
                        }
                    }
                    
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
    Logout view to blacklist the refresh token and clear httpOnly cookies.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Get refresh token from cookie
        refresh_token = request.COOKIES.get("refresh_token")
        
        if not refresh_token:
            # Fallback to request body for backward compatibility
            refresh_token = request.data.get("refresh")
        
        response = Response({"detail": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
        
        # Clear httpOnly cookies
        response.delete_cookie('access_token', samesite='Lax')
        response.delete_cookie('refresh_token', samesite='Lax')
        
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                # Still log the error but don't fail logout
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Token blacklist failed: {str(e)}")
        
        return response


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom JWT refresh view that works with httpOnly cookies.
    """
    def post(self, request, *args, **kwargs):
        # Get refresh token from cookie
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return Response(
                {'detail': 'Refresh token not found in cookies'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Add refresh token to request data
        request.data['refresh'] = refresh_token
        
        # Call parent method
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_200_OK:
            # Set new access token in httpOnly cookie
            access_token = response.data.get('access')
            new_refresh_token = response.data.get('refresh')
            
            if access_token:
                response.set_cookie(
                    'access_token',
                    access_token,
                    max_age=settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME').total_seconds(),
                    httponly=True,
                    secure=not settings.DEBUG,
                    samesite='Lax'
                )
            
            if new_refresh_token:
                response.set_cookie(
                    'refresh_token',
                    new_refresh_token,
                    max_age=settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME').total_seconds(),
                    httponly=True,
                    secure=not settings.DEBUG,
                    samesite='Lax'
                )
            
            # Remove tokens from response body
            response.data = {
                'detail': 'Token refresh successful'
            }
        
        return response


@method_decorator(ratelimit(key='ip', rate='3/m', method='POST', block=True), name='post')
class UserRegistrationView(APIView):
    """
    User registration view. Creates inactive user and sends verification email.
    Rate limited to 3 attempts per minute per IP.
    """
    permission_classes = []  # Allow anonymous access
    
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                user = serializer.save()
                
                # Create verification token
                verification_token = EmailVerificationToken.objects.db_manager('accounts').create(
                    user=user
                )
                
                # Send verification email (if email settings are configured)
                self.send_verification_email(user, verification_token.token)
                
                return Response({
                    "detail": "Registration successful. Please check your email to verify your account.",
                    "email": user.email
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return handle_validation_error(
                    detail="Registration failed. Please try again.",
                    log_message=f"Registration error: {str(e)}"
                )
        
        return handle_validation_error(
            detail="Registration failed due to invalid data.",
            errors=serializer.errors
        )
    
    def send_verification_email(self, user, token):
        """Send verification email to user"""
        try:
            # Get frontend URL from settings or environment
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            verification_url = f"{frontend_url}/verify-email?token={token}"
            
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
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@observer.com'),
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            # Log error but don't fail registration
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send verification email to {user.email}: {str(e)}")


class EmailVerificationView(APIView):
    """
    Email verification view. Verifies token and allows password setup.
    """
    permission_classes = []  # Allow anonymous access
    
    def post(self, request, *args, **kwargs):
        serializer = EmailVerificationSerializer(data=request.data)
        
        if serializer.is_valid():
            token = serializer.validated_data['token']
            password = serializer.validated_data['password']
            
            try:
                # Find verification token
                verification_token = EmailVerificationToken.objects.using('accounts').get(
                    token=token
                )
                
                # Check if token is valid
                if not verification_token.is_valid():
                    return handle_validation_error(
                        detail="Invalid or expired verification token."
                    )
                
                # Activate user and set password
                user = verification_token.user
                user.is_active = True
                user.set_password(password)
                user.save(using='accounts')
                
                # Mark token as used
                verification_token.is_used = True
                verification_token.save(using='accounts')
                
                return Response({
                    "detail": "Email verified successfully. You can now log in.",
                    "email": user.email
                }, status=status.HTTP_200_OK)
                
            except EmailVerificationToken.DoesNotExist:
                return handle_validation_error(
                    detail="Invalid verification token."
                )
            except Exception as e:
                return handle_validation_error(
                    detail="Email verification failed. Please try again.",
                    log_message=f"Email verification error: {str(e)}"
                )
        
        return handle_validation_error(
            detail="Email verification failed due to invalid data.",
            errors=serializer.errors
        )
