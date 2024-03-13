from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, ProviderViewSet, DepartmentViewSet, MultiModalDataPathViewSet, EncounterViewSet
from .views import GraphPatientViewSet, GraphProviderViewSet, GraphDepartmentViewSet, GraphEncounterViewSet, DepartmentEncountersView

router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'providers', ProviderViewSet, basename='provider')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'datapaths', MultiModalDataPathViewSet, basename='datapath')
router.register(r'encounters', EncounterViewSet, basename='encounter')
router.register(r'graphpatients', GraphPatientViewSet, basename='graphpatient')
router.register(r'graphproviders', GraphProviderViewSet,
                basename='graphprovider')
router.register(r'graphdepartments', GraphDepartmentViewSet,
                basename='graphdepartment')
router.register(r'graphencounters', GraphEncounterViewSet,
                basename='graphencounter')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/department-encounters/<str:department_name>/',
         DepartmentEncountersView.as_view()),
]
