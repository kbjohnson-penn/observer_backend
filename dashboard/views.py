from rest_framework import viewsets
from rest_framework import permissions

from .models import Patient, Provider, Department, MultiModalDataPath, Encounter
from .serializers import PatientSerializer, ProviderSerializer, DepartmentSerializer, MultiModalDataPathSerializer, EncounterSerializer


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [ReadOnly]


class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [ReadOnly]


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [ReadOnly]


class MultiModalDataPathViewSet(viewsets.ModelViewSet):
    queryset = MultiModalDataPath.objects.all()
    serializer_class = MultiModalDataPathSerializer
    permission_classes = [ReadOnly]


class EncounterViewSet(viewsets.ModelViewSet):
    queryset = Encounter.objects.all()
    serializer_class = EncounterSerializer
    permission_classes = [ReadOnly]
