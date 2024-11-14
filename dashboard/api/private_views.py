from rest_framework import viewsets
from rest_framework import permissions

from ..models import Patient, Provider, EncounterSource, Department, MultiModalData, Encounter
from ..serializers import PatientSerializer, ProviderSerializer, MultiModalDataSerializer, EncounterSerializer, EncounterSourceSerializer, DepartmentSerializer


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [permissions.IsAuthenticated]


class EncounterSourceViewSet(viewsets.ModelViewSet):
    queryset = EncounterSource.objects.all()
    serializer_class = EncounterSourceSerializer
    permission_classes = [permissions.IsAuthenticated]


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class MultiModalDataViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MultiModalData.objects.all()
    serializer_class = MultiModalDataSerializer
    permission_classes = [permissions.IsAuthenticated]


class EncounterViewSet(viewsets.ModelViewSet):
    queryset = Encounter.objects.all()
    serializer_class = EncounterSerializer
    permission_classes = [permissions.IsAuthenticated]
