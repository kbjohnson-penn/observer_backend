from django.urls import path

from accounts.api.views.profile_views import ProfileView

urlpatterns = [
    path("", ProfileView.as_view(), name="api_profile"),
]
