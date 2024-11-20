from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .private_views import PatientViewSet, ProviderViewSet, DepartmentViewSet, MultiModalDataViewSet, EncounterViewSet, EncounterSourceViewSet, EncounterFileViewSet
from .public_views import PublicPatientViewSet, PublicProviderViewSet, PublicDepartmentViewSet, PublicEncounterSourceViewSet, PublicEncounterViewSet, PublicMultiModalDataViewSet
from .user_views import register, profile

router = DefaultRouter()

# Public routes
router.register(r'public/encountersources',
                PublicEncounterSourceViewSet, basename='public-encountersource')
router.register(r'public/departments', PublicDepartmentViewSet,
                basename='public-department')
router.register(r'public/providers', PublicProviderViewSet,
                basename='public-provider')
router.register(r'public/patients', PublicPatientViewSet,
                basename='public-patient')
router.register(r'public/mmdata', PublicMultiModalDataViewSet,
                basename='public-mmdata')
router.register(r'public/encounters', PublicEncounterViewSet,
                basename='public-encounter')

# Private routes
router.register(r'encountersources', EncounterSourceViewSet,
                basename='encountersource')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'providers', ProviderViewSet, basename='provider')
router.register(r'mmdata', MultiModalDataViewSet, basename='mmdata')
router.register(r'encounters', EncounterViewSet, basename='encounter')
router.register(r'encounterfiles', EncounterFileViewSet,
                basename='encounterfile')

urlpatterns = [
    path('', include(router.urls)),
    # path('auth/register/', register, name='api_register'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', profile, name='api_profile'),
]
