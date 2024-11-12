from rest_framework import serializers
from ..models import Encounter, MultiModalData


class MultiModalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiModalData
        fields = ['id', 'provider_view', 'patient_view', 'room_view',
                  'audio', 'transcript', 'patient_survey', 'provider_survey', 'patient_annotation', 'provider_annotation', 'rias_transcript', 'rias_codes']


class EncounterSerializer(serializers.ModelSerializer):
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
            'provider_satisfaction', 'is_deidentified', 'is_restricted'
        ]

    def get_patient_id(self, obj):
        return obj.patient.id if obj.patient else None

    def get_provider_id(self, obj):
        return obj.provider.id if obj.provider else None

    def get_multi_modal_data_id(self, obj):
        return obj.multi_modal_data.id if obj.multi_modal_data else None
