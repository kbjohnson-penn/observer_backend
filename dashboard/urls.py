from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, ProviderViewSet, DepartmentViewSet, MultiModalDataPathViewSet, EncounterViewSet, AnonymizedMappingViewSet

router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'providers', ProviderViewSet, basename='provider')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'datapaths', MultiModalDataPathViewSet, basename='datapath')
router.register(r'encounters', EncounterViewSet, basename='encounter')
router.register(r'anonymizedmappings', AnonymizedMappingViewSet, basename='anonymizedmapping')

urlpatterns = [
    path('api/', include(router.urls)),
]