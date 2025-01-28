from .base import BaseAuthenticatedViewSet, HasAccessToEncounter, filter_queryset_by_user_tier
from dashboard.models import Encounter
from dashboard.api.serializers import EncounterSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404


class EncounterViewSet(BaseAuthenticatedViewSet):
    serializer_class = EncounterSerializer
    permission_classes = [HasAccessToEncounter]

    def get_queryset(self):
        return filter_queryset_by_user_tier(
            Encounter.objects.all().select_related(
                'tier', 'patient', 'provider', 'department', 'encounter_source'),
            self.request.user
        )

    def get_object(self):
        try:
            encounter = Encounter.objects.get(pk=self.kwargs['pk'])
            self.check_object_permissions(self.request, encounter)
            return encounter
        except Encounter.DoesNotExist:
            raise Http404

    def retrieve(self, request, *args, **kwargs):
        try:
            encounter = self.get_object()
            serializer = self.get_serializer(encounter)
            return Response(serializer.data)
        except Http404:
            return Response(
                {"detail": f"Encounter with ID {kwargs['pk']} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
