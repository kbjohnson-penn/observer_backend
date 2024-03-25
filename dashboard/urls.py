from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, ProviderViewSet, DepartmentViewSet, MultiModalDataPathViewSet, EncounterViewSet
from .views import GetKnowledgeGraph

router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'providers', ProviderViewSet, basename='provider')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'datapaths', MultiModalDataPathViewSet, basename='datapath')
router.register(r'encounters', EncounterViewSet, basename='encounter')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/knowledge-graph/', GetKnowledgeGraph.as_view(), name='knowledge_graph'),
]
