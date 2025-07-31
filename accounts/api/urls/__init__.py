from django.urls import path, include

app_name = 'accounts_api'

urlpatterns = [
    path('auth/', include('accounts.api.urls.auth_urls')),
    path('profile/', include('accounts.api.urls.profile_urls')),
]