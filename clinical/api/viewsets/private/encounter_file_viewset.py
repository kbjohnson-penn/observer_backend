import logging

from django.http import Http404, StreamingHttpResponse

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from clinical.api.serializers.encounter_serializers import EncounterFileSerializer
from clinical.models import EncounterFile
from clinical.storage_backend import AzureDataLakeStorage
from shared.api.permissions import (
    BaseAuthenticatedViewSet,
    HasAccessToEncounter,
    filter_queryset_by_user_tier,
)

logger = logging.getLogger(__name__)


class EncounterFileViewSet(BaseAuthenticatedViewSet):
    """
    Viewset for managing EncounterFile objects with access control.
    """

    serializer_class = EncounterFileSerializer
    permission_classes = [HasAccessToEncounter]

    def get_queryset(self):
        """
        Return only EncounterFile instances accessible to the user based on their tier.
        """
        return filter_queryset_by_user_tier(
            EncounterFile.objects.using("clinical").select_related("encounter").all(),
            self.request.user,
            related_field="encounter__tier_level",
        ).order_by("-id")

    def get_object(self):
        """
        Fetch the EncounterFile object or raise 404 if not found or inaccessible.
        """
        try:
            obj = self.get_queryset().get(pk=self.kwargs["pk"])
            self.check_object_permissions(self.request, obj)
            return obj
        except EncounterFile.DoesNotExist:
            raise Http404(f"EncounterFile with ID {self.kwargs['pk']} not found.")

    @action(detail=True, methods=["get"], url_path="stream")
    def stream_file(self, request, pk=None):
        """
        Stream the specified file if the user has access to it.
        """
        try:
            encounter_file = self.get_object()
            file_path = encounter_file.file_path

            # Initialize AzureDataLakeStorage
            storage = AzureDataLakeStorage()
            file_client = storage.file_system_client.get_file_client(file_path)

            # Stream the file
            download = file_client.download_file()
            file_stream = download.chunks()
            content_type = storage._get_content_type(file_path)

            response = StreamingHttpResponse(file_stream, content_type=content_type)
            response["Content-Disposition"] = f'inline; filename="{file_client.path_name}"'
            return response
        except Exception as e:
            # Log full error for debugging, return generic message
            logger.error(f"File streaming error for pk={pk}: {str(e)}")
            raise Http404("File not found or inaccessible")

    @action(detail=True, methods=["get"], url_path="download")
    def download_file(self, request, pk=None):
        """
        Download the specified file if the user has access to it.
        """
        try:
            encounter_file = self.get_object()
            file_path = encounter_file.file_path

            # Initialize AzureDataLakeStorage
            storage = AzureDataLakeStorage()
            file_client = storage.file_system_client.get_file_client(file_path)

            # Stream the file for download
            download = file_client.download_file()
            file_stream = download.chunks()
            content_type = storage._get_content_type(file_path)

            response = StreamingHttpResponse(file_stream, content_type=content_type)
            response["Content-Disposition"] = f'attachment; filename="{file_client.path_name}"'
            return response
        except Exception as e:
            # Log full error for debugging, return generic message
            logger.error(f"File download error for pk={pk}: {str(e)}")
            raise Http404("File not found or inaccessible")

    @action(detail=False, methods=["post"], url_path="by-ids")
    def get_files_by_ids(self, request):
        """
        Fetch multiple files by their IDs.
        """
        ids = request.data.get("ids", [])
        if not ids:
            return Response({"detail": "No IDs provided."}, status=status.HTTP_400_BAD_REQUEST)

        files = self.get_queryset().filter(id__in=ids)
        serializer = self.get_serializer(files, many=True)
        return Response(serializer.data)
