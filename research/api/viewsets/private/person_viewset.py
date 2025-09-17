from shared.api.permissions import BaseAuthenticatedViewSet, filter_queryset_by_user_tier
from research.models import Person, VisitOccurrence
from research.api.serializers import PersonSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404


class PersonViewSet(BaseAuthenticatedViewSet):
    serializer_class = PersonSerializer

    def get_queryset(self):
        accessible_visits = filter_queryset_by_user_tier(
            VisitOccurrence.objects.using('research').all(), 
            self.request.user, 
            related_field='tier_id'
        )
        return Person.objects.using('research').filter(
            visitoccurrence__in=accessible_visits
        ).distinct()

    def get_object(self):
        """
        Get a person object respecting tier-based access control.
        """
        queryset = self.get_queryset()
        try:
            person = queryset.get(pk=self.kwargs['pk'])
            self.check_object_permissions(self.request, person)
            return person
        except Person.DoesNotExist:
            raise Http404
        
    def retrieve(self, request, *args, **kwargs):
        try:
            person = self.get_object()
            serializer = self.get_serializer(person)
            return Response(serializer.data)
        except Http404:
            return Response(
                {"detail": f"Person with ID {kwargs['pk']} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )