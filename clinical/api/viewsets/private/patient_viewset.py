from django.http import Http404

from rest_framework import status
from rest_framework.response import Response

from clinical.api.serializers.patient_serializers import PatientSerializer
from clinical.models import Encounter, Patient
from shared.api.permissions import (
    BaseAuthenticatedViewSet,
    HasAccessToEncounter,
    filter_queryset_by_user_tier,
)


class PatientViewSet(BaseAuthenticatedViewSet):
    serializer_class = PatientSerializer
    permission_classes = [HasAccessToEncounter]

    def get_queryset(self):
        accessible_encounters = filter_queryset_by_user_tier(
            Encounter.objects.using("clinical").all(), self.request.user, related_field="tier_id"
        )
        return (
            Patient.objects.using("clinical")
            .filter(encounter__in=accessible_encounters)
            .distinct()
            .order_by("id")
        )

    def get_object(self):
        try:
            patient = Patient.objects.using("clinical").get(pk=self.kwargs["pk"])
            self.check_object_permissions(self.request, patient)
            return patient
        except Patient.DoesNotExist:
            raise Http404

    def retrieve(self, request, *args, **kwargs):
        try:
            patient = self.get_object()
            serializer = self.get_serializer(patient)
            return Response(serializer.data)
        except Http404:
            return Response(
                {"detail": "Resource not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
