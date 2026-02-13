from clinical.api.serializers.department_serializers import (
    DepartmentSerializer,
    EncounterSourceSerializer,
)
from clinical.models import Department, EncounterSource
from shared.api.permissions import BaseAuthenticatedViewSet


class EncounterSourceViewSet(BaseAuthenticatedViewSet):
    queryset = EncounterSource.objects.using("clinical").all().order_by("id")
    serializer_class = EncounterSourceSerializer


class DepartmentViewSet(BaseAuthenticatedViewSet):
    queryset = Department.objects.using("clinical").all().order_by("id")
    serializer_class = DepartmentSerializer
