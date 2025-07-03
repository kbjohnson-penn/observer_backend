from rest_framework.routers import DefaultRouter
from dashboard.api.viewsets.public import (
    PublicPatientViewSet,
    PublicProviderViewSet,
    PublicDepartmentViewSet,
    PublicEncounterSourceViewSet,
    PublicEncounterViewSet,
    PublicMultiModalDataViewSet,
)
from dashboard.api.views.sample_data_views import SampleDataViewSet

router = DefaultRouter()

# Public routes
router.register(r'encountersources',
                PublicEncounterSourceViewSet, basename='v1-public-encountersource')
router.register(r'departments', PublicDepartmentViewSet,
                basename='v1-public-department')
router.register(r'providers', PublicProviderViewSet,
                basename='v1-public-provider')
router.register(r'patients', PublicPatientViewSet,
                basename='v1-public-patient')
router.register(r'mmdata', PublicMultiModalDataViewSet,
                basename='v1-public-mmdata')
router.register(r'encounters', PublicEncounterViewSet,
                basename='v1-public-encounter')
router.register(r'sample-data', SampleDataViewSet,
                basename='v1-public-sample-data')

urlpatterns = router.urls
