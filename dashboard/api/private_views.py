from rest_framework import status
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import StreamingHttpResponse, Http404
from django.conf import settings
from azure.storage.filedatalake import DataLakeServiceClient
from azure.core.exceptions import ResourceNotFoundError
from ..models import (
    Patient, Provider, EncounterSource, Department, MultiModalData, Encounter, EncounterFile, Tier
)
from ..serializers import (
    PatientSerializer, ProviderSerializer, MultiModalDataSerializer, EncounterSerializer,
    EncounterSourceSerializer, DepartmentSerializer, EncounterFileSerializer
)
from ..storage_backend import AzureDataLakeStorage
import logging

logger = logging.getLogger(__name__)


def filter_queryset_by_user_tier(queryset, user):
    """
    Filters a queryset based on the user's tier level.
    """
    if user.is_superuser:
        return queryset
    if hasattr(user, 'profile') and user.profile.tier:
        user_tier = user.profile.tier
        accessible_tiers = Tier.objects.filter(level__lte=user_tier.level)
        return queryset.filter(tier__in=accessible_tiers)
    return queryset.none()


class BaseAuthenticatedViewSet(ReadOnlyModelViewSet):
    """
    A base viewset that applies read-only access and authenticated permissions to all derived viewsets.
    """
    permission_classes = [IsAuthenticated]

    def has_access_to_tier(self, user, tier):
        """
        Check if the user has access to the specified tier.
        """
        if user.is_superuser:
            return True
        if hasattr(user, 'profile') and user.profile.tier:
            user_tier = user.profile.tier
            return tier.level <= user_tier.level
        return False


class HasAccessToEncounter(BasePermission):
    """
    Custom permission to check access to objects based on encounters.
    """

    def has_object_permission(self, request, view, obj):
        # Directly check the tier for Encounter objects
        if isinstance(obj, Encounter):
            return view.has_access_to_tier(request.user, obj.tier)

        # For Patient and Provider, check encounters linked to the object
        if isinstance(obj, Patient):
            encounters = Encounter.objects.filter(patient=obj)
        elif isinstance(obj, Provider):
            encounters = Encounter.objects.filter(provider=obj)
        else:
            return False

        return any(view.has_access_to_tier(request.user, encounter.tier) for encounter in encounters)


class PatientViewSet(BaseAuthenticatedViewSet):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, HasAccessToEncounter]

    def get_queryset(self):
        """
        Return only patients associated with encounters the user has access to.
        """
        accessible_encounters = filter_queryset_by_user_tier(
            Encounter.objects.all(), self.request.user)
        return Patient.objects.filter(encounter__in=accessible_encounters).distinct()

    def get_object(self):
        """
        Fetch the patient object or raise 404 if not found.
        """
        try:
            patient = Patient.objects.get(pk=self.kwargs['pk'])
            self.check_object_permissions(self.request, patient)
            return patient
        except Patient.DoesNotExist:
            raise Http404  # DRF will handle this and return a 404 response.

    def retrieve(self, request, *args, **kwargs):
        """
        Handle the detail view for a specific patient.
        """
        try:
            patient = self.get_object()
            serializer = self.get_serializer(patient)
            return Response(serializer.data)
        except Http404:
            return Response(
                {"detail": f"Patient with ID {kwargs['pk']} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class ProviderViewSet(BaseAuthenticatedViewSet):
    serializer_class = ProviderSerializer
    permission_classes = [IsAuthenticated, HasAccessToEncounter]

    def get_queryset(self):
        """
        Return only providers associated with encounters the user has access to.
        """
        accessible_encounters = filter_queryset_by_user_tier(
            Encounter.objects.all(), self.request.user)
        return Provider.objects.filter(encounter__in=accessible_encounters).distinct()

    def get_object(self):
        """
        Fetch the provider object or raise 404 if not found.
        """
        try:
            provider = Provider.objects.get(pk=self.kwargs['pk'])
            self.check_object_permissions(self.request, provider)
            return provider
        except Provider.DoesNotExist:
            raise Http404  # DRF will handle this and return a 404 response.

    def retrieve(self, request, *args, **kwargs):
        """
        Handle the detail view for a specific provider.
        """
        try:
            provider = self.get_object()
            serializer = self.get_serializer(provider)
            return Response(serializer.data)
        except Http404:
            return Response(
                {"detail": f"Provider with ID {kwargs['pk']} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class EncounterSourceViewSet(BaseAuthenticatedViewSet):
    queryset = EncounterSource.objects.all()
    serializer_class = EncounterSourceSerializer


class DepartmentViewSet(BaseAuthenticatedViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class MultiModalDataViewSet(BaseAuthenticatedViewSet):
    """
    A viewset for viewing MultiModalData instances (read-only and filtered by user access).
    """
    serializer_class = MultiModalDataSerializer

    def get_queryset(self):
        """
        Return only MultiModalData instances accessible to the user based on their tier.
        """
        # Get accessible encounters for the user
        accessible_encounters = filter_queryset_by_user_tier(Encounter.objects.all(), self.request.user)

        # Filter MultiModalData linked to those encounters
        return MultiModalData.objects.filter(encounter__in=accessible_encounters).distinct()

    def get_object(self):
        """
        Fetch a single MultiModalData instance or raise a detailed error.
        """
        queryset = self.get_queryset()
        multimodal_data_id = self.kwargs.get('pk')

        try:
            # Attempt to retrieve the object from the filtered queryset
            return queryset.get(pk=multimodal_data_id)
        except MultiModalData.DoesNotExist:
            # Raise 404 if the object does not exist or is not accessible
            raise Http404

    def retrieve(self, request, *args, **kwargs):
        """
        Handle the detail view for a specific MultiModalData instance.
        """
        try:
            # Retrieve the object using get_object
            multimodal_data = self.get_object()
            serializer = self.get_serializer(multimodal_data)
            return Response(serializer.data)
        except Http404 as e:
            # Return custom 404 error response
            return Response(
                {"detail": f"MultiModalData with ID {kwargs['pk']} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class EncounterViewSet(BaseAuthenticatedViewSet):
    serializer_class = EncounterSerializer
    permission_classes = [IsAuthenticated, HasAccessToEncounter]

    def get_queryset(self):
        """
        Return only encounters accessible to the user based on their tier.
        """
        return filter_queryset_by_user_tier(
            Encounter.objects.all().select_related(
                'tier', 'patient', 'provider', 'department', 'encounter_source'),
            self.request.user
        )

    def get_object(self):
        """
        Fetch the encounter object or raise 404 if not found.
        """
        try:
            encounter = Encounter.objects.get(pk=self.kwargs['pk'])
            self.check_object_permissions(self.request, encounter)
            return encounter
        except Encounter.DoesNotExist:
            raise Http404  # DRF will handle this and return a 404 response.

    def retrieve(self, request, *args, **kwargs):
        """
        Handle the detail view for a specific encounter.
        """
        try:
            encounter = self.get_object()
            serializer = self.get_serializer(encounter)
            return Response(serializer.data)
        except Http404:
            return Response(
                {"detail": f"Encounter with ID {kwargs['pk']} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class EncounterFileViewSet(ReadOnlyModelViewSet):
    queryset = EncounterFile.objects.all()
    serializer_class = EncounterFileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return EncounterFile.objects.all()
        if hasattr(user, 'profile') and user.profile.tier:
            user_tier = user.profile.tier
            accessible_tiers = Tier.objects.filter(level__lte=user_tier.level)
            return EncounterFile.objects.filter(encounter__tier__in=accessible_tiers)
        return EncounterFile.objects.none()

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

            # Stream the file
            download = file_client.download_file()
            file_stream = download.chunks()

            response = StreamingHttpResponse(
                file_stream, content_type=content_type)
            response['Content-Disposition'] = f'inline; filename="\
                {file_client.path_name}"'
            return response
        except Exception as e:
            raise Http404(f"File not found: {str(e)}")

    @action(detail=True, methods=['get'], url_path='download')
    def download_file(self, request, pk=None):
        try:
            encounter_file = self.get_object()
            file_path = encounter_file.file_path

            # Check if the user has access to the tier
            if not self.has_access_to_tier(request.user, encounter_file.encounter.tier):
                return Response({"detail": "You do not have access to this file."}, status=status.HTTP_403_FORBIDDEN)

            # Initialize AzureDataLakeStorage
            storage = AzureDataLakeStorage()
            file_client = storage.file_system_client.get_file_client(file_path)

            # Determine the content type based on the file extension
            content_type = storage._get_content_type(file_path)

            # Stream the file
            download = file_client.download_file()
            file_stream = download.chunks()

            response = StreamingHttpResponse(
                file_stream, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="\
                {file_client.path_name}"'
            return response
        except Exception as e:
            raise Http404(f"File not found: {str(e)}")

    @action(detail=False, methods=['post'], url_path='by-ids')
    def get_files_by_ids(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"detail": "No IDs provided."}, status=status.HTTP_400_BAD_REQUEST)
        files = self.get_queryset().filter(id__in=ids)
        serializer = self.get_serializer(files, many=True)
        return Response(serializer.data)
