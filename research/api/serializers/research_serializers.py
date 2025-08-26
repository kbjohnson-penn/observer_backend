from rest_framework import serializers
from research.models import (
    Person, Provider, VisitOccurrence, Note, ConditionOccurrence,
    DrugExposure, ProcedureOccurrence, Measurement, Observation,
    PatientSurvey, ProviderSurvey, Concept, AuditLogs
)


class PersonSerializer(serializers.ModelSerializer):
    """Serializer for Person model in research database."""
    
    class Meta:
        model = Person
        fields = '__all__'


class ProviderSerializer(serializers.ModelSerializer):
    """Serializer for Provider model in research database."""
    
    class Meta:
        model = Provider
        fields = '__all__'


class VisitOccurrenceSerializer(serializers.ModelSerializer):
    """Serializer for VisitOccurrence model in research database."""
    
    class Meta:
        model = VisitOccurrence
        fields = '__all__'


class ConceptSerializer(serializers.ModelSerializer):
    """Serializer for Concept model in research database."""
    
    class Meta:
        model = Concept
        fields = '__all__'


class NoteSerializer(serializers.ModelSerializer):
    """Serializer for Note model in research database."""
    
    class Meta:
        model = Note
        fields = '__all__'


class ConditionOccurrenceSerializer(serializers.ModelSerializer):
    """Serializer for ConditionOccurrence model in research database."""
    
    class Meta:
        model = ConditionOccurrence
        fields = '__all__'


class DrugExposureSerializer(serializers.ModelSerializer):
    """Serializer for DrugExposure model in research database."""
    
    class Meta:
        model = DrugExposure
        fields = '__all__'


class ProcedureOccurrenceSerializer(serializers.ModelSerializer):
    """Serializer for ProcedureOccurrence model in research database."""
    
    class Meta:
        model = ProcedureOccurrence
        fields = '__all__'


class MeasurementSerializer(serializers.ModelSerializer):
    """Serializer for Measurement model in research database."""
    
    class Meta:
        model = Measurement
        fields = '__all__'


class ObservationSerializer(serializers.ModelSerializer):
    """Serializer for Observation model in research database."""
    
    class Meta:
        model = Observation
        fields = '__all__'


class PatientSurveySerializer(serializers.ModelSerializer):
    """Serializer for PatientSurvey model in research database."""
    
    class Meta:
        model = PatientSurvey
        fields = '__all__'


class ProviderSurveySerializer(serializers.ModelSerializer):
    """Serializer for ProviderSurvey model in research database."""
    
    class Meta:
        model = ProviderSurvey
        fields = '__all__'


class AuditLogsSerializer(serializers.ModelSerializer):
    """Serializer for AuditLogs model in research database."""
    
    class Meta:
        model = AuditLogs
        fields = '__all__'
        read_only_fields = ['id', 'access_time', 'user_id', 'workstation_id', 
                           'access_action', 'metric_id', 'metric_name', 'metric_desc', 
                           'metric_type', 'metric_group', 'event_action_type', 
                           'event_action_subtype']