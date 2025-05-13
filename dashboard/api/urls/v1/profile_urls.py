from django.urls import path
from dashboard.api.views.profile_views import ProfileView

urlpatterns = [
    path('', ProfileView.as_view(), name='api_profile'),
]
