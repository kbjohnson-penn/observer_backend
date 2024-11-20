from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import StreamingHttpResponse, Http404
from django.conf import settings
from azure.storage.filedatalake import DataLakeServiceClient
from ..models import Patient, Provider, EncounterSource, Department, MultiModalData, Encounter, EncounterFile, Tier
from ..serializers import PatientSerializer, ProviderSerializer, MultiModalDataSerializer, EncounterSerializer, EncounterSourceSerializer, DepartmentSerializer, EncounterFileSerializer
from ..storage_backend import AzureDataLakeStorage


class BaseAuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]


class PatientViewSet(BaseAuthenticatedViewSet):
    serializer_class = PatientSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Patient.objects.all()
        if hasattr(user, 'profile') and user.profile.tier:
            user_tier = user.profile.tier
            # Get all tiers below or equal to the user's tier
            accessible_tiers = Tier.objects.filter(level__lte=user_tier.level)
            return Patient.objects.filter(encounter__tier__in=accessible_tiers)
        return Patient.objects.none()


class ProviderViewSet(BaseAuthenticatedViewSet):
    serializer_class = ProviderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Provider.objects.all()
        if hasattr(user, 'profile') and user.profile.tier:
            user_tier = user.profile.tier
            # Get all tiers below or equal to the user's tier
            accessible_tiers = Tier.objects.filter(level__lte=user_tier.level)
            return Provider.objects.filter(encounter__tier__in=accessible_tiers)
        return Provider.objects.none()


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


class EncounterViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EncounterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Encounter.objects.all().select_related('tier')
        if hasattr(user, 'profile') and user.profile.tier:
            user_tier = user.profile.tier
            # Get all tiers below or equal to the user's tier
            accessible_tiers = Tier.objects.filter(level__lte=user_tier.level)
            return Encounter.objects.filter(tier__in=accessible_tiers).select_related('tier')
        return Encounter.objects.none()


class EncounterFileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EncounterFile.objects.all()
    serializer_class = EncounterFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return EncounterFile.objects.all()
        if hasattr(user, 'profile') and user.profile.tier:
            user_tier = user.profile.tier
            # Get all tiers below or equal to the user's tier
            accessible_tiers = Tier.objects.filter(level__lte=user_tier.level)
            return EncounterFile.objects.filter(encounter__tier__in=accessible_tiers)
        return EncounterFile.objects.none()

    @action(detail=False, methods=['post'], url_path='by-ids')
    def get_files_by_ids(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"detail": "No IDs provided."}, status=status.HTTP_400_BAD_REQUEST)
        files = self.get_queryset().filter(id__in=ids)
        serializer = self.get_serializer(files, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='stream')
    def stream_file(self, request, pk=None):
        try:
            encounter_file = self.get_object()
            file_path = encounter_file.file_path

            # Check if the user has access to the tier
            if not self._has_access_to_tier(request.user, encounter_file.encounter.tier):
                return Response({"detail": "You do not have access to this file."}, status=status.HTTP_403_FORBIDDEN)

            # Initialize AzureDataLakeStorage
            storage = AzureDataLakeStorage()
            file_client = storage.file_system_client.get_file_client(file_path)

            # Determine the content type based on the file extension
            content_type = storage._get_content_type(file_path)

            # Download the file in chunks
            download = file_client.download_file()
            file_stream = download.chunks()

            response = StreamingHttpResponse(
                file_stream, content_type=content_type)
            response['Content-Disposition'] = f'inline; filename="{file_client.path_name}"'
            return response
        except Exception as e:
            raise Http404(f"File not found: {str(e)}")

    @action(detail=True, methods=['get'], url_path='download')
    def download_file(self, request, pk=None):
        try:
            encounter_file = self.get_object()
            file_path = encounter_file.file_path

            # Check if the user has access to the tier
            if not self._has_access_to_tier(request.user, encounter_file.encounter.tier):
                return Response({"detail": "You do not have access to this file."}, status=status.HTTP_403_FORBIDDEN)

            # Initialize AzureDataLakeStorage
            storage = AzureDataLakeStorage()
            file_client = storage.file_system_client.get_file_client(file_path)

            # Determine the content type based on the file extension
            content_type = storage._get_content_type(file_path)

            # Download the file in chunks
            download = file_client.download_file()
            file_stream = download.chunks()

            response = StreamingHttpResponse(
                file_stream, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{file_client.path_name}"'
            return response
        except Exception as e:
            raise Http404(f"File not found: {str(e)}")

    def _has_access_to_tier(self, user, tier):
        if user.is_superuser:
            return True
        if hasattr(user, 'profile') and user.profile.tier:
            user_tier = user.profile.tier
            return tier.level <= user_tier.level
        return False
