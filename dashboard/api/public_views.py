from rest_framework import viewsets
from rest_framework import permissions

from ..models import Patient, Provider, Department, MultiModalData, Encounter, EncounterSource
from ..serializers import PublicPatientSerializer, PublicProviderSerializer, PublicEncounterSerializer, PublicDepartmentSerializer, MultiModalDataSerializer, PublicEncounterSourceSerializer


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class BasePublicReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [ReadOnly]


class PublicEncounterSourceViewSet(BasePublicReadOnlyViewSet):
    queryset = EncounterSource.objects.all()
    serializer_class = PublicEncounterSourceSerializer


class PublicPatientViewSet(BasePublicReadOnlyViewSet):
    queryset = Patient.objects.all()
    serializer_class = PublicPatientSerializer


class PublicProviderViewSet(BasePublicReadOnlyViewSet):
    queryset = Provider.objects.all()
    serializer_class = PublicProviderSerializer


class PublicEncounterViewSet(BasePublicReadOnlyViewSet):
    queryset = Encounter.objects.all()
    serializer_class = PublicEncounterSerializer


class PublicDepartmentViewSet(BasePublicReadOnlyViewSet):
    queryset = Department.objects.all()
    serializer_class = PublicDepartmentSerializer


class PublicMultiModalDataViewSet(BasePublicReadOnlyViewSet):
    queryset = MultiModalData.objects.all()
    serializer_class = MultiModalDataSerializer
