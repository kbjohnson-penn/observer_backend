from rest_framework.response import Response

from clinical.api.serializers.encounter_serializers import EncounterSerializer
from clinical.models import Encounter
from shared.api.error_handlers import ErrorHandlerMixin, ObserverNotFound, handle_not_found
from shared.api.permissions import (
    BaseAuthenticatedViewSet,
    HasAccessToEncounter,
    filter_queryset_by_user_tier,
)


class EncounterViewSet(BaseAuthenticatedViewSet, ErrorHandlerMixin):
    serializer_class = EncounterSerializer
    permission_classes = [HasAccessToEncounter]

    def get_queryset(self):
        return filter_queryset_by_user_tier(
            Encounter.objects.using("clinical")
            .all()
            .select_related(
                "patient", "provider", "department", "encounter_source", "multi_modal_data"
            )
            .prefetch_related("files"),
            self.request.user,
            related_field="tier_id",
        ).order_by("-encounter_date_and_time", "-id")

    def get_object(self):
        try:
            # Use the filtered queryset to ensure tier-based access control
            queryset = self.get_queryset()
            encounter = queryset.get(pk=self.kwargs["pk"])
            self.check_object_permissions(self.request, encounter)
            return encounter
        except Encounter.DoesNotExist:
            from shared.api.error_handlers import ObserverNotFound

            raise ObserverNotFound(detail=f"Encounter with ID {self.kwargs['pk']} not found.")

    def retrieve(self, request, *args, **kwargs):
        try:
            encounter = self.get_object()
            serializer = self.get_serializer(encounter)
            return Response(serializer.data)
        except ObserverNotFound as e:
            return handle_not_found(detail=str(e.detail))
