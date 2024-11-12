from rest_framework import viewsets
from rest_framework import permissions

from ..models import Patient, Provider, EncounterSource, Department, MultiModalData, Encounter
from ..serializers import (PatientSerializer, PublicPatientSerializer, ProviderSerializer, PublicProviderSerializer,
                           MultiModalDataSerializer, EncounterSerializer, PublicDepartmentSerializer,
                           EncounterSourceSerializer, DepartmentSerializer)


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]


class PublicPatientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PublicPatientSerializer
    permission_classes = [ReadOnly]


class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [permissions.IsAuthenticated]


class PublicProviderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = PublicProviderSerializer
    permission_classes = [ReadOnly]


class EncounterSourceViewSet(viewsets.ModelViewSet):
    queryset = EncounterSource.objects.all()
    serializer_class = EncounterSourceSerializer
    permission_classes = [ReadOnly]


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class PulicDepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.all()
    serializer_class = PublicDepartmentSerializer
    permission_classes = [ReadOnly]


class MultiModalDataViewSet(viewsets.ModelViewSet):
    queryset = MultiModalData.objects.all()
    serializer_class = MultiModalDataSerializer
    permission_classes = [ReadOnly]


class EncounterViewSet(viewsets.ModelViewSet):
    queryset = Encounter.objects.all()
    serializer_class = EncounterSerializer
    permission_classes = [ReadOnly]
