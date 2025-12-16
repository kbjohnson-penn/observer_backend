from django.urls import path

from accounts.api.views.auth_views import (
    CSRFTokenView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    EmailVerificationView,
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    UserRegistrationView,
)

urlpatterns = [
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", CustomTokenVerifyView.as_view(), name="token_verify"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", UserRegistrationView.as_view(), name="user_registration"),
    path("verify-email/", EmailVerificationView.as_view(), name="email_verification"),
    path("change-password/", PasswordChangeView.as_view(), name="password_change"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password_reset_request"),
    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("csrf-token/", CSRFTokenView.as_view(), name="csrf_token"),
]
