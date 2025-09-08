from shared.api.permissions import BaseAuthenticatedViewSet, filter_queryset_by_user_tier
from research.models import VisitOccurrence
from research.api.serializers import VisitOccurrenceSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404


class VisitOccurrenceViewSet(BaseAuthenticatedViewSet):
    serializer_class = VisitOccurrenceSerializer

    def get_queryset(self):
        return filter_queryset_by_user_tier(
            VisitOccurrence.objects.using('research').select_related('person', 'provider').all(),
            self.request.user,
            related_field='tier_id'
        )

    def get_object(self):
        queryset = self.get_queryset()
        try:
            visit = queryset.get(pk=self.kwargs['pk'])
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