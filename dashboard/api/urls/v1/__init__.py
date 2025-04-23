from django.urls import path, include

urlpatterns = [
    # path('private/', include('dashboard.api.urls.v1.private_urls')),
    path('public/', include('dashboard.api.urls.v1.public_urls')),
    # path('auth/', include('dashboard.api.urls.v1.auth_urls')),
    # path('profile/', include('dashboard.api.urls.v1.profile_urls')),
]
