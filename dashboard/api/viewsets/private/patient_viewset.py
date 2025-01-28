from .base import BaseAuthenticatedViewSet, HasAccessToEncounter, filter_queryset_by_user_tier
from dashboard.models import Patient, Encounter
from dashboard.api.serializers import PatientSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404


class PatientViewSet(BaseAuthenticatedViewSet):
    serializer_class = PatientSerializer
    permission_classes = [HasAccessToEncounter]

    def get_queryset(self):
        accessible_encounters = filter_queryset_by_user_tier(
            Encounter.objects.all(), self.request.user)
        return Patient.objects.filter(encounter__in=accessible_encounters).distinct()

    def get_object(self):
        try:
            patient = Patient.objects.get(pk=self.kwargs['pk'])
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
                {"detail": f"Patient with ID {kwargs['pk']} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
