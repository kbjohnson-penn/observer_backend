from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EncounterViewSet, DepartmentViewSet, ChoiceViewSet

router = DefaultRouter()
router.register(r'encounters', EncounterViewSet, basename='encounter')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'media_choices', ChoiceViewSet, basename='media_choice')


urlpatterns = [
    path('api/', include(router.urls)),
]