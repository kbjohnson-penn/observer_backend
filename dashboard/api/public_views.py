from rest_framework import viewsets
from rest_framework import permissions

from ..models import Patient, Provider, Department, MultiModalData, Encounter, EncounterSource
from ..serializers import PublicPatientSerializer, PublicProviderSerializer, PublicEncounterSerializer, PublicDepartmentSerializer, PublicMultiModalDataSerializer, PublicEncounterSourceSerializer


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class PublicEncounterSourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EncounterSource.objects.all()
    serializer_class = PublicEncounterSourceSerializer
    permission_classes = [ReadOnly]


class PublicPatientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PublicPatientSerializer
    permission_classes = [ReadOnly]


class PublicProviderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = PublicProviderSerializer
    permission_classes = [ReadOnly]


class PublicEncounterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Encounter.objects.all()
    serializer_class = PublicEncounterSerializer
    permission_classes = [ReadOnly]


class PublicDepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.all()
    serializer_class = PublicDepartmentSerializer
    permission_classes = [ReadOnly]


class PublicMultiModalDataViewSet(viewsets.ModelViewSet):
    queryset = MultiModalData.objects.all()
    serializer_class = PublicMultiModalDataSerializer
    permission_classes = [ReadOnly]
