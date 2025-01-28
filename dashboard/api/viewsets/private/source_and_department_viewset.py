from .base import BaseAuthenticatedViewSet, HasAccessToEncounter, filter_queryset_by_user_tier
from dashboard.models import EncounterSource, Department
from dashboard.api.serializers import EncounterSourceSerializer, DepartmentSerializer


class EncounterSourceViewSet(BaseAuthenticatedViewSet):
    queryset = EncounterSource.objects.all()
    serializer_class = EncounterSourceSerializer


class DepartmentViewSet(BaseAuthenticatedViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
