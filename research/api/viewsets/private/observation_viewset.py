from shared.api.permissions import BaseAuthenticatedViewSet, filter_queryset_by_user_tier
from research.models import Observation, VisitOccurrence
from research.api.serializers import ObservationSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404


class ObservationViewSet(BaseAuthenticatedViewSet):
    serializer_class = ObservationSerializer

    def get_queryset(self):
        accessible_visits = filter_queryset_by_user_tier(
            VisitOccurrence.objects.using('research').all(), 
            self.request.user, 
            related_field='tier_id'
        )
        return Observation.objects.using('research').filter(
            visit_occurrence__in=accessible_visits
        ).distinct()

    def get_object(self):
        queryset = self.get_queryset()
        try:
            observation = queryset.get(pk=self.kwargs['pk'])
            self.check_object_permissions(self.request, observation)
            return observation
        except Observation.DoesNotExist:
            raise Http404
        
    def retrieve(self, request, *args, **kwargs):
        try:
            observation = self.get_object()
            serializer = self.get_serializer(observation)
            return Response(serializer.data)
        except Http404:
            return Response(
                {"detail": f"Observation with ID {kwargs['pk']} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )