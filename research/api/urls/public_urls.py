from django.urls import path

from rest_framework.routers import DefaultRouter

from research.api.views.sample_data_views import PublicVideoStreamView, SampleDataView

router = DefaultRouter()

# URL patterns for API views (non-ViewSet views)
urlpatterns = [
    path("sample-data/", SampleDataView.as_view(), name="v1-public-sample-data"),
    path("video/<path:file_path>/", PublicVideoStreamView.as_view(), name="v1-public-media-stream"),
] + router.urls
