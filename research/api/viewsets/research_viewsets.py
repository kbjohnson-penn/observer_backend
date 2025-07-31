from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from research.models import Person, Provider, VisitOccurrence, Concept
from research.api.serializers.research_serializers import (
    PersonSerializer, ProviderSerializer, VisitOccurrenceSerializer, ConceptSerializer
)


class BaseResearchViewSet(ReadOnlyModelViewSet):
    """Base viewset for research models with proper database routing."""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Ensure all queries use the research database."""
        return super().get_queryset().using('research')


class PersonViewSet(BaseResearchViewSet):
    """ViewSet for Person model in research database."""
    queryset = Person.objects.using('research').all()
    serializer_class = PersonSerializer


class ProviderViewSet(BaseResearchViewSet):
    """ViewSet for Provider model in research database."""
    queryset = Provider.objects.using('research').all()
    serializer_class = ProviderSerializer


class VisitOccurrenceViewSet(BaseResearchViewSet):
    """ViewSet for VisitOccurrence model in research database."""
    queryset = VisitOccurrence.objects.using('research').select_related('person_id', 'provider_id').all()
    serializer_class = VisitOccurrenceSerializer


class ConceptViewSet(BaseResearchViewSet):
    """ViewSet for Concept model in research database."""
    queryset = Concept.objects.using('research').all()
    serializer_class = ConceptSerializer


# Additional viewsets can be added for other research models as needed
# Corresponding serializers have been created in research_serializers.py