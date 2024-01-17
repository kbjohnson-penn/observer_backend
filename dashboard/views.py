from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Encounter, Department, ENCOUNTER_MEDIA_TYPE_CHOICES, Choice
from .serializers import EncounterSerializer, DepartmentSerializer, ChoiceSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = {item['id']: item['name'] for item in serializer.data}
        return Response(data)

class EncounterViewSet(viewsets.ModelViewSet):
    queryset = Encounter.objects.all()
    serializer_class = EncounterSerializer


class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = {item['id']: item['name'] for item in serializer.data}
        return Response(data)
