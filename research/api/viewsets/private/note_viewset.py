from django.http import Http404

from rest_framework import status
from rest_framework.response import Response

from research.api.serializers import NoteSerializer
from research.models import Note, VisitOccurrence
from shared.api.permissions import BaseAuthenticatedViewSet, filter_queryset_by_user_tier


class NoteViewSet(BaseAuthenticatedViewSet):
    serializer_class = NoteSerializer

    def get_queryset(self):
        accessible_visits = filter_queryset_by_user_tier(
            VisitOccurrence.objects.using("research").select_related("person", "provider").all(),
            self.request.user,
            related_field="tier_level",
        )
        return (
            Note.objects.using("research")
            .filter(visit_occurrence__in=accessible_visits)
            .select_related("visit_occurrence")
            .distinct()
            .order_by("-id")
        )

    def get_object(self):
        queryset = self.get_queryset()
        try:
            note = queryset.get(pk=self.kwargs["pk"])
            self.check_object_permissions(self.request, note)
            return note
        except Note.DoesNotExist:
            raise Http404

    def retrieve(self, request, *args, **kwargs):
        try:
            note = self.get_object()
            serializer = self.get_serializer(note)
            return Response(serializer.data)
        except Http404:
            return Response(
                {"detail": f"Note with ID {kwargs['pk']} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
