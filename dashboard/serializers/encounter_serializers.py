from rest_framework import serializers
from ..models import Encounter, MultiModalData, Department, EncounterSource, Provider, Patient, EncounterFile


class MultiModalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiModalData
        fields = '__all__'


class EncounterFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EncounterFile
        fields = '__all__'


class EncounterSerializer(serializers.ModelSerializer):
    encounter_source = serializers.PrimaryKeyRelatedField(
        queryset=EncounterSource.objects.all())
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all())
    provider = serializers.PrimaryKeyRelatedField(
        queryset=Provider.objects.all())
    patient = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all())
    encounterfile_ids = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, source='files')

    class Meta:
        model = Encounter
        fields = [
            'id', 'csn_number', 'case_id', 'encounter_source', 'department',
            'provider', 'patient', 'encounter_date_and_time', 'provider_satisfaction',
            'patient_satisfaction', 'is_deidentified', 'is_restricted', 'type', 'encounterfile_ids'
        ]


class PublicEncounterSerializer(serializers.ModelSerializer):
    encounter_source = serializers.StringRelatedField()
    department = serializers.StringRelatedField()
    patient_id = serializers.SerializerMethodField()
    provider_id = serializers.SerializerMethodField()
    multi_modal_data_id = serializers.SerializerMethodField()

    class Meta:
        model = Encounter
        fields = [
            'id', 'provider_id', 'patient_id', 'encounter_source', 'department',
            'multi_modal_data_id', 'encounter_date_and_time', 'patient_satisfaction',
            'provider_satisfaction', 'is_deidentified', 'is_restricted', 'type'
        ]

    def get_patient_id(self, obj):
        return obj.patient.id if obj.patient else None

    def get_provider_id(self, obj):
        return obj.provider.id if obj.provider else None

    def get_multi_modal_data_id(self, obj):
        return obj.multi_modal_data.id if obj.multi_modal_data else None
