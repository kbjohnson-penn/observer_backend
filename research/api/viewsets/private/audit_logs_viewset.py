from shared.api.permissions import BaseAuthenticatedViewSet, filter_queryset_by_user_tier
from research.models import AuditLogs, VisitOccurrence
from research.api.serializers import AuditLogsSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404


class AuditLogsViewSet(BaseAuthenticatedViewSet):
    serializer_class = AuditLogsSerializer

    def get_queryset(self):
        accessible_visits = filter_queryset_by_user_tier(
            VisitOccurrence.objects.using('research').all(),
            self.request.user,
            related_field='tier_id'
        )
        return AuditLogs.objects.using('research').filter(
            visit_occurrence__in=accessible_visits
        ).distinct()

    def get_object(self):
        queryset = self.get_queryset()
        try:
            audit_log = queryset.get(pk=self.kwargs['pk'])
            self.check_object_permissions(self.request, audit_log)
            return audit_log
        except AuditLogs.DoesNotExist:
            raise Http404

    def retrieve(self, request, *args, **kwargs):
        try:
            audit_log = self.get_object()
            serializer = self.get_serializer(audit_log)
            return Response(serializer.data)
        except Http404:
            return Response(
                {"detail": f"AuditLogs with ID {kwargs['pk']} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )