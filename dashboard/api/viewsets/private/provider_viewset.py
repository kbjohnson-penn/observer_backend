from .base import BaseAuthenticatedViewSet, HasAccessToEncounter, filter_queryset_by_user_tier
from dashboard.models import Provider, Encounter
from dashboard.api.serializers import ProviderSerializer
from rest_framework.response import Response
from django.http import Http404
from rest_framework import status


class ProviderViewSet(BaseAuthenticatedViewSet):
    serializer_class = ProviderSerializer
    permission_classes = [HasAccessToEncounter]

    def get_queryset(self):
        accessible_encounters = filter_queryset_by_user_tier(
            Encounter.objects.all(), self.request.user)
        return Provider.objects.filter(encounter__in=accessible_encounters).distinct()

    def get_object(self):
        try:
            provider = Provider.objects.get(pk=self.kwargs['pk'])
            self.check_object_permissions(self.request, provider)
            return provider
        except Provider.DoesNotExist:
            raise Http404

    def retrieve(self, request, *args, **kwargs):
        try:
            provider = self.get_object()
            serializer = self.get_serializer(provider)
            return Response(serializer.data)
        except Http404:
            return Response(
                {"detail": f"Provider with ID {kwargs['pk']} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
