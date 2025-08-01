from django.urls import path
from accounts.api.views.auth_views import (
    CustomTokenObtainPairView, 
    CustomTokenRefreshView,
    LogoutView, 
    UserRegistrationView,
    EmailVerificationView,
    CSRFTokenView
)
from rest_framework_simplejwt.views import TokenVerifyView

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', UserRegistrationView.as_view(), name='user_registration'),
    path('verify-email/', EmailVerificationView.as_view(), name='email_verification'),
    path('csrf-token/', CSRFTokenView.as_view(), name='csrf_token'),
]
