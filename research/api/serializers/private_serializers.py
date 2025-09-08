from rest_framework import serializers
from research.models import (
    Person, Provider, VisitOccurrence
)


class PersonSerializer(serializers.ModelSerializer):
    """Private serializer for Person model - full access for authenticated users."""
    
    class Meta:
        model = Person
        fields = '__all__'


class ProviderSerializer(serializers.ModelSerializer):
    """Private serializer for Provider model - full access for authenticated users."""
    
    class Meta:
        model = Provider
        fields = '__all__'


class VisitOccurrenceSerializer(serializers.ModelSerializer):
    """Private serializer for VisitOccurrence model - full access with related data."""
    
    class Meta:
        model = VisitOccurrence
        fields = '__all__'


