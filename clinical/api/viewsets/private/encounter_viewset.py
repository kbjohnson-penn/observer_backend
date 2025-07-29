from shared.api.permissions import BaseAuthenticatedViewSet, HasAccessToEncounter, filter_queryset_by_user_tier
from shared.api.error_handlers import ErrorHandlerMixin, handle_not_found, safe_get_object_or_404, ObserverNotFound
from clinical.models import Encounter
from clinical.api.serializers.encounter_serializers import EncounterSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404


class EncounterViewSet(BaseAuthenticatedViewSet, ErrorHandlerMixin):
    serializer_class = EncounterSerializer
    permission_classes = [HasAccessToEncounter]

    def get_queryset(self):
        return filter_queryset_by_user_tier(
            Encounter.objects.using('clinical').all().select_related(
                'patient', 'provider', 'department', 'encounter_source', 'multi_modal_data'
            ).prefetch_related('files'),
            self.request.user,
            related_field='tier_id'
        )

    def get_object(self):
        try:
            encounter = safe_get_object_or_404(
                Encounter.objects.using('clinical'), 
                error_message=f"Encounter with ID {self.kwargs['pk']} not found.",
                pk=self.kwargs['pk']
            )
            self.check_object_permissions(self.request, encounter)
            return encounter
        except ObserverNotFound:
            raise

    def retrieve(self, request, *args, **kwargs):
        try:
            encounter = self.get_object()
            serializer = self.get_serializer(encounter)
            return Response(serializer.data)
        except ObserverNotFound as e:
            return handle_not_found(detail=str(e.detail))
