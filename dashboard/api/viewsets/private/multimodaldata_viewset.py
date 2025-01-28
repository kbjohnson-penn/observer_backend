from .base import BaseAuthenticatedViewSet, filter_queryset_by_user_tier
from dashboard.models import MultiModalData, Encounter
from dashboard.api.serializers import MultiModalDataSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404


class MultiModalDataViewSet(BaseAuthenticatedViewSet):
    serializer_class = MultiModalDataSerializer

    def get_queryset(self):
        accessible_encounters = filter_queryset_by_user_tier(
            Encounter.objects.all(), self.request.user)
        return MultiModalData.objects.filter(encounter__in=accessible_encounters).distinct()

    def get_object(self):
        try:
            multimodal_data = self.get_queryset().get(pk=self.kwargs['pk'])
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
