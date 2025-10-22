from django.urls import include, path

app_name = "accounts_api"

urlpatterns = [
    path("auth/", include("accounts.api.urls.auth_urls")),
    path("profile/", include("accounts.api.urls.profile_urls")),
    path("agreements/", include("accounts.api.urls.agreement_urls")),
]
