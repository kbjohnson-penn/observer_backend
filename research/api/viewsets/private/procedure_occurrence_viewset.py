from shared.api.permissions import BaseAuthenticatedViewSet, filter_queryset_by_user_tier
from research.models import ProcedureOccurrence, VisitOccurrence
from research.api.serializers import ProcedureOccurrenceSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404


class ProcedureOccurrenceViewSet(BaseAuthenticatedViewSet):
    serializer_class = ProcedureOccurrenceSerializer

    def get_queryset(self):
        accessible_visits = filter_queryset_by_user_tier(
            VisitOccurrence.objects.using('research')
                .select_related('person', 'provider')
                .all(),
            self.request.user,
            related_field='tier_id'
        )
        return ProcedureOccurrence.objects.using('research').filter(
            visit_occurrence__in=accessible_visits
        ).select_related('visit_occurrence').distinct().order_by('-id')

    def get_object(self):
        queryset = self.get_queryset()
        try:
            procedure_occurrence = queryset.get(pk=self.kwargs['pk'])
            self.check_object_permissions(self.request, procedure_occurrence)
            return procedure_occurrence
        except ProcedureOccurrence.DoesNotExist:
            raise Http404
        
    def retrieve(self, request, *args, **kwargs):
        try:
            procedure_occurrence = self.get_object()
            serializer = self.get_serializer(procedure_occurrence)
            return Response(serializer.data)
        except Http404:
            return Response(
                {"detail": f"ProcedureOccurrence with ID {kwargs['pk']} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )