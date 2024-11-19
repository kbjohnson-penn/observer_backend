from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User

from ..models import Patient, Provider, EncounterSource, Department, MultiModalData, Encounter, EncounterFile
from ..serializers import PatientSerializer, ProviderSerializer, MultiModalDataSerializer, EncounterSerializer, EncounterSourceSerializer, DepartmentSerializer, EncounterFileSerializer


class BaseAuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]


class PatientViewSet(BaseAuthenticatedViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class ProviderViewSet(BaseAuthenticatedViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer


class EncounterSourceViewSet(BaseAuthenticatedViewSet):
    queryset = EncounterSource.objects.all()
    serializer_class = EncounterSourceSerializer


class DepartmentViewSet(BaseAuthenticatedViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class MultiModalDataViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MultiModalData.objects.all()
    serializer_class = MultiModalDataSerializer
    permission_classes = [permissions.IsAuthenticated]


class EncounterViewSet(BaseAuthenticatedViewSet):
    serializer_class = EncounterSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Encounter.objects.all().select_related('tier')
        if hasattr(user, 'profile') and user.profile.tier:
            user_tier = user.profile.tier
            return Encounter.objects.filter(tier=user_tier).select_related('tier')
        return Encounter.objects.none()


class EncounterFileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EncounterFile.objects.all()
    serializer_class = EncounterFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='by-ids')
    def get_files_by_ids(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"detail": "No IDs provided."}, status=status.HTTP_400_BAD_REQUEST)
        files = EncounterFile.objects.filter(id__in=ids)
        serializer = self.get_serializer(files, many=True)
        return Response(serializer.data)
