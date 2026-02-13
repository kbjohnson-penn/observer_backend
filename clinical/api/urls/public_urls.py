from rest_framework.routers import DefaultRouter

from clinical.api.viewsets.public import (
    PublicDepartmentViewSet,
    PublicEncounterSourceViewSet,
    PublicEncounterViewSet,
    PublicMultiModalDataViewSet,
    PublicPatientViewSet,
    PublicProviderViewSet,
)

router = DefaultRouter()

# Public routes for clinical data - proper database routing
router.register(
    r"encountersources", PublicEncounterSourceViewSet, basename="v1-public-clinical-encountersource"
)
router.register(r"departments", PublicDepartmentViewSet, basename="v1-public-clinical-department")
router.register(r"providers", PublicProviderViewSet, basename="v1-public-clinical-provider")
router.register(r"patients", PublicPatientViewSet, basename="v1-public-clinical-patient")
router.register(r"mmdata", PublicMultiModalDataViewSet, basename="v1-public-clinical-mmdata")
router.register(r"encounters", PublicEncounterViewSet, basename="v1-public-clinical-encounter")

urlpatterns = router.urls
