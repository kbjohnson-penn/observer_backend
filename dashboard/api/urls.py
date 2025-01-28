from django.urls import path, include

urlpatterns = [
    # Include API versioned URLs
    path('api/', include('dashboard.api.urls')),
]
