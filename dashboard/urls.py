from django.urls import path, include

urlpatterns = [
    path('api/', include('dashboard.api.urls')),
    # Other URLs for the dashboard app
]
