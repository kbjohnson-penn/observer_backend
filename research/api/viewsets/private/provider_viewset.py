from shared.api.permissions import BaseAuthenticatedViewSet, filter_queryset_by_user_tier
from research.models import Provider, VisitOccurrence
from research.api.serializers import ProviderSerializer
from django.http import Http404


class ProviderViewSet(BaseAuthenticatedViewSet):
    serializer_class = ProviderSerializer

    def get_queryset(self):
        accessible_visits = filter_queryset_by_user_tier(
            VisitOccurrence.objects.using('research').all(), 
            self.request.user, 
            related_field='tier_id'
        )
        return Provider.objects.using('research').filter(
            visitoccurrence__in=accessible_visits
        ).distinct()

    def get_object(self):
        queryset = self.get_queryset()
        try:
            provider = queryset.get(pk=self.kwargs['pk'])
            self.check_object_permissions(self.request, provider)
            return provider
        except Provider.DoesNotExist:
            raise Http404