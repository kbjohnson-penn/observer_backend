from django.http import Http404

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from research.api.serializers import VisitOccurrenceSerializer
from research.api.serializers.private_serializers import (
    ConditionOccurrenceSerializer,
    DrugExposureSerializer,
    MeasurementSerializer,
    NoteSerializer,
    ObservationSerializer,
    ProcedureOccurrenceSerializer,
)
from research.models import (
    ConditionOccurrence,
    DrugExposure,
    Measurement,
    Note,
    Observation,
    ProcedureOccurrence,
    VisitOccurrence,
)
from shared.api.permissions import BaseAuthenticatedViewSet, filter_queryset_by_user_tier


class VisitOccurrenceViewSet(BaseAuthenticatedViewSet):
    serializer_class = VisitOccurrenceSerializer

    def get_queryset(self):
        return filter_queryset_by_user_tier(
            VisitOccurrence.objects.using("research").select_related("person", "provider").all(),
            self.request.user,
            related_field="tier_level",
        ).order_by("-visit_start_date", "-id")

    def get_object(self):
        queryset = self.get_queryset()
        try:
            visit = queryset.get(pk=self.kwargs["pk"])
            self.check_object_permissions(self.request, visit)
            return visit
        except VisitOccurrence.DoesNotExist:
            raise Http404

    def retrieve(self, request, *args, **kwargs):
        try:
            visit = self.get_object()
            serializer = self.get_serializer(visit)
            return Response(serializer.data)
        except Http404:
            return Response(
                {"detail": f"Visit Occurrence with ID {kwargs['pk']} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["get"], url_path="detail-data")
    def detail_data(self, request, *args, **kwargs):
        """Return all related data for a single visit in one response."""
        try:
            visit = self.get_object()
        except Http404:
            return Response(
                {"detail": f"Visit Occurrence with ID {kwargs['pk']} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        vid = visit.id

        conditions = (
            ConditionOccurrence.objects.using("research")
            .filter(visit_occurrence_id=vid)
            .order_by("-is_primary_dx", "id")
        )

        drugs = (
            DrugExposure.objects.using("research").filter(visit_occurrence_id=vid).order_by("id")
        )

        procedures = (
            ProcedureOccurrence.objects.using("research")
            .filter(visit_occurrence_id=vid)
            .order_by("id")
        )

        notes = Note.objects.using("research").filter(visit_occurrence_id=vid).order_by("id")

        observations = (
            Observation.objects.using("research").filter(visit_occurrence_id=vid).order_by("id")
        )

        measurements = (
            Measurement.objects.using("research").filter(visit_occurrence_id=vid).order_by("id")
        )

        # Serialize each queryset once; derive count from the result to avoid
        # an extra .count() DB query per section (was 12 queries, now 6).
        conditions_data = ConditionOccurrenceSerializer(conditions, many=True).data
        drugs_data = DrugExposureSerializer(drugs, many=True).data
        procedures_data = ProcedureOccurrenceSerializer(procedures, many=True).data
        notes_data = NoteSerializer(notes, many=True).data
        observations_data = ObservationSerializer(observations, many=True).data
        measurements_data = MeasurementSerializer(measurements, many=True).data

        return Response(
            {
                "visit": VisitOccurrenceSerializer(visit).data,
                "conditions": {"count": len(conditions_data), "results": conditions_data},
                "drugs": {"count": len(drugs_data), "results": drugs_data},
                "procedures": {"count": len(procedures_data), "results": procedures_data},
                "notes": {"count": len(notes_data), "results": notes_data},
                "observations": {"count": len(observations_data), "results": observations_data},
                "measurements": {"count": len(measurements_data), "results": measurements_data},
            }
        )
