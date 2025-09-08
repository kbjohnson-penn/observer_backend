from rest_framework.routers import DefaultRouter
from research.api.viewsets.private import (
    PersonViewSet,
    ProviderViewSet,
    VisitOccurrenceViewSet,
)

router = DefaultRouter()

# Register all research model viewsets
router.register(r'persons', PersonViewSet, basename='v1-research-person')
router.register(r'research-providers', ProviderViewSet, basename='v1-research-provider')
router.register(r'visits', VisitOccurrenceViewSet, basename='v1-research-visit')

urlpatterns = router.urls