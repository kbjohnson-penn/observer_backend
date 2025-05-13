from rest_framework.routers import DefaultRouter
from dashboard.api.viewsets.private import (
    PatientViewSet,
    ProviderViewSet,
    DepartmentViewSet,
    MultiModalDataViewSet,
    EncounterViewSet,
    EncounterSourceViewSet,
    EncounterFileViewSet,
)

router = DefaultRouter()

router.register(r'encountersources', EncounterSourceViewSet,
                basename='v1-encountersource')
router.register(r'departments', DepartmentViewSet, basename='v1-department')
router.register(r'patients', PatientViewSet, basename='v1-patient')
router.register(r'providers', ProviderViewSet, basename='v1-provider')
router.register(r'mmdata', MultiModalDataViewSet, basename='v1-mmdata')
router.register(r'encounters', EncounterViewSet, basename='v1-encounter')
router.register(r'encounterfiles', EncounterFileViewSet,
                basename='v1-encounterfile')

urlpatterns = router.urls
