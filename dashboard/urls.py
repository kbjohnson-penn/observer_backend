from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EncounterViewSet, DepartmentViewSet

router = DefaultRouter()
router.register(r'encounters', EncounterViewSet, basename='encounter')
router.register(r'departments', DepartmentViewSet, basename='department')

urlpatterns = [
    path('api/', include(router.urls)),
]