from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (PatientViewSet, PublicPatientViewSet, ProviderViewSet, PublicProviderViewSet, PulicDepartmentViewSet,
                    DepartmentViewSet, MultiModalDataViewSet, EncounterViewSet, EncounterSourceViewSet)
from .auth_views import register, profile
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()

# Public routes
router.register(r'public/encountersources',
                EncounterSourceViewSet, basename='public-encountersource')
router.register(r'public/departments', PulicDepartmentViewSet,
                basename='public-department')
router.register(r'public/providers', PublicProviderViewSet,
                basename='public-provider')
router.register(r'public/patients', PublicPatientViewSet,
                basename='public-patient')

# Private routes
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'providers', ProviderViewSet, basename='provider')
router.register(r'encountersources', EncounterSourceViewSet,
                basename='encountersource')
router.register(r'datapaths', MultiModalDataViewSet, basename='datapath')
router.register(r'encounters', EncounterViewSet, basename='encounter')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', register, name='api_register'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', profile, name='api_profile'),
]
