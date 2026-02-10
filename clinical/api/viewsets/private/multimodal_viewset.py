from django.http import Http404

from rest_framework import status
from rest_framework.response import Response

from clinical.api.serializers.encounter_serializers import MultiModalDataSerializer
from clinical.models import Encounter, MultiModalData
from shared.api.permissions import BaseAuthenticatedViewSet, filter_queryset_by_user_tier


class MultiModalDataViewSet(BaseAuthenticatedViewSet):
    serializer_class = MultiModalDataSerializer

    def get_queryset(self):
        accessible_encounters = filter_queryset_by_user_tier(
            Encounter.objects.using("clinical").all(), self.request.user, related_field="tier_level"
        )
        return (
            MultiModalData.objects.using("clinical")
            .select_related("encounter")
            .filter(encounter__in=accessible_encounters)
            .distinct()
            .order_by("-id")
        )

    def get_object(self):
        try:
            multimodal_data = self.get_queryset().get(pk=self.kwargs["pk"])
            return multimodal_data
        except MultiModalData.DoesNotExist:
            raise Http404

    def retrieve(self, request, *args, **kwargs):
        try:
            multimodal_data = self.get_object()
            serializer = self.get_serializer(multimodal_data)
            return Response(serializer.data)
        except Http404:
            return Response(
                {"detail": f"MultiModalData with ID {kwargs['pk']} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
