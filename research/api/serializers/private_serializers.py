from rest_framework import serializers
from research.models import (
    Person, 
    Provider, 
    VisitOccurrence, 
    Note, 
    ConditionOccurrence,
    DrugExposure,
    ProcedureOccurrence,
    Observation,
    Measurement,
    AuditLogs,
    PatientSurvey,
    ProviderSurvey,
    Labs
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


class NoteSerializer(serializers.ModelSerializer):
    """Private serializer for Note model - full access for authenticated users."""
    
    class Meta:
        model = Note
        fields = '__all__'


class ConditionOccurrenceSerializer(serializers.ModelSerializer):
    """Private serializer for ConditionOccurrence model - full access for authenticated users."""
    
    class Meta:
        model = ConditionOccurrence
        fields = '__all__'


class DrugExposureSerializer(serializers.ModelSerializer):
    """Private serializer for DrugExposure model - full access for authenticated users."""
    
    class Meta:
        model = DrugExposure
        fields = '__all__'


class ProcedureOccurrenceSerializer(serializers.ModelSerializer):
    """Private serializer for ProcedureOccurrence model - full access for authenticated users."""
    
    class Meta:
        model = ProcedureOccurrence
        fields = '__all__'


class ObservationSerializer(serializers.ModelSerializer):
    """Private serializer for Observation model - full access for authenticated users."""
    
    class Meta:
        model = Observation
        fields = '__all__'


class MeasurementSerializer(serializers.ModelSerializer):
    """Private serializer for Measurement model - full access for authenticated users."""
    
    class Meta:
        model = Measurement
        fields = '__all__'


class AuditLogsSerializer(serializers.ModelSerializer):
    """Private serializer for AuditLogs model - full access for authenticated users."""
    
    class Meta:
        model = AuditLogs
        fields = '__all__'


class PatientSurveySerializer(serializers.ModelSerializer):
    """Private serializer for PatientSurvey model - full access for authenticated users."""
    
    class Meta:
        model = PatientSurvey
        fields = '__all__'


class ProviderSurveySerializer(serializers.ModelSerializer):
    """Private serializer for ProviderSurvey model - full access for authenticated users."""
    
    class Meta:
        model = ProviderSurvey
        fields = '__all__'


class LabsSerializer(serializers.ModelSerializer):
    """Private serializer for Labs model - full access for authenticated users."""
    
    class Meta:
        model = Labs
        fields = '__all__'