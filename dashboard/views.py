from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Patient, Provider, Department, MultiModalDataPath, Encounter
from .serializers import PatientSerializer, ProviderSerializer, DepartmentSerializer, MultiModalDataPathSerializer, EncounterSerializer


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class MultiModalDataPathViewSet(viewsets.ModelViewSet):
    queryset = MultiModalDataPath.objects.all()
    serializer_class = MultiModalDataPathSerializer


class EncounterViewSet(viewsets.ModelViewSet):
    queryset = Encounter.objects.all()
    serializer_class = EncounterSerializer
