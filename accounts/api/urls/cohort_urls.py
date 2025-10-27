from rest_framework.routers import DefaultRouter

from accounts.api.viewsets.cohort_viewset import CohortViewSet

router = DefaultRouter()
router.register(r"", CohortViewSet, basename="cohort")

urlpatterns = router.urls
