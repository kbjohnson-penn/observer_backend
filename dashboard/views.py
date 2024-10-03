from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Patient, Provider, EncounterSource, Department, MultiModalDataPath, Encounter, EncounterSimCenter, EncounterRIAS
from .serializers import PatientSerializer, ProviderSerializer, EncounterSourceSerializer, DepartmentSerializer, MultiModalDataPathSerializer, EncounterSerializer, EncounterSimCenterSerializer, EncounterRIASSerializer


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


class EncounterSourceViewSet(viewsets.ModelViewSet):
    queryset = EncounterSource.objects.all()
    serializer_class = EncounterSourceSerializer
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


class EncounterSimCenterViewSet(viewsets.ModelViewSet):
    queryset = EncounterSimCenter.objects.all()
    serializer_class = EncounterSimCenterSerializer
    permission_classes = [ReadOnly]


class EncounterRIASViewSet(viewsets.ModelViewSet):
    queryset = EncounterRIAS.objects.all()
    serializer_class = EncounterRIASSerializer
    permission_classes = [ReadOnly]
