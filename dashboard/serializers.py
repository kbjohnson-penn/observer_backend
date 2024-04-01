from rest_framework import serializers
from .models import Patient, Provider, Department, MultiModalDataPath, Encounter, EncounterSource

BOOLEAN_CHOICES = {
    True: 'Yes',
    False: 'No',
}


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['patient_id', 'date_of_birth', 'sex', 'race', 'ethnicity']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['race'] = 'UN' if rep.get('race') == '' else rep['race']
        rep['sex'] = 'UN' if rep.get('sex') == '' else rep['sex']
        rep['ethnicity'] = 'UN' if rep.get(
            'ethnicity') == '' else rep['ethnicity']
        return rep


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ['provider_id', 'date_of_birth', 'sex', 'race', 'ethnicity']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['race'] = 'UN' if rep.get('race') == '' else rep['race']
        rep['sex'] = 'UN' if rep.get('sex') == '' else rep['sex']
        rep['ethnicity'] = 'UN' if rep.get(
            'ethnicity') == '' else rep['ethnicity']
        return rep


class EncounterSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EncounterSource
        fields = ['name']


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['name']


class MultiModalDataPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiModalDataPath
        fields = ['multi_modal_data_id', 'provider_view', 'patient_view', 'room_view',
                  'audio', 'transcript', 'patient_survey', 'provider_survey', 'rias_transcript', 'rias_codes']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        for field in ['provider_view', 'patient_view', 'room_view', 'audio', 'transcript', 'patient_survey', 'provider_survey', 'rias_transcript', 'rias_codes']:
            rep[field] = bool(rep[field])
        return rep


class EncounterSerializer(serializers.ModelSerializer):
    encounter_source = serializers.StringRelatedField()
    department = serializers.StringRelatedField()
    patient = serializers.StringRelatedField()
    provider = serializers.StringRelatedField()
    multi_modal_data = serializers.StringRelatedField()

    class Meta:
        model = Encounter
        fields = ['case_id', 'provider', 'patient', 'encounter_source', 'department', 'multi_modal_data',
                  'encounter_date_and_time', 'patient_satisfaction', 'provider_satisfaction', 'is_deidentified', 'is_restricted']


class NodeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    labels = serializers.ListField(child=serializers.CharField())
    properties = serializers.DictField(child=serializers.JSONField())


class EdgeSerializer(serializers.Serializer):
    source = serializers.IntegerField()
    target = serializers.IntegerField()
    type = serializers.CharField()
    properties = serializers.DictField(child=serializers.JSONField())


class GraphSerializer(serializers.Serializer):
    nodes = NodeSerializer(many=True)
    edges = EdgeSerializer(many=True)
