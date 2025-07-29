from shared.api.permissions import BaseAuthenticatedViewSet, HasAccessToEncounter, filter_queryset_by_user_tier
from clinical.models import EncounterSource, Department
from clinical.api.serializers.department_serializers import EncounterSourceSerializer, DepartmentSerializer


class EncounterSourceViewSet(BaseAuthenticatedViewSet):
    queryset = EncounterSource.objects.using('clinical').all()
    serializer_class = EncounterSourceSerializer


class DepartmentViewSet(BaseAuthenticatedViewSet):
    queryset = Department.objects.using('clinical').all()
    serializer_class = DepartmentSerializer
