from rest_framework import serializers
from datetime import date
from dateutil.relativedelta import relativedelta
from .models import (
    Patient, Provider, Department, MultiModalDataPath, Encounter,
    EncounterSource, EncounterSimCenter, EncounterRIAS
)

def calculate_age(date_of_birth):
    if date_of_birth is None:
        return None
    today = date.today()
    return relativedelta(today, date_of_birth).years


class EncounterSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EncounterSource
        fields = ['name']


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['name']


class ProviderSerializer(serializers.ModelSerializer):
    year_of_birth = serializers.SerializerMethodField()

    class Meta:
        model = Provider
        fields = ['id', 'provider_id', 'year_of_birth', 'sex', 'race', 'ethnicity']

    def get_year_of_birth(self, instance):
        age = calculate_age(instance.date_of_birth)
        if age is None:
            return None
        if age > 89:
            max_year_of_birth = date.today().year - 89
            return str(max_year_of_birth)
        return str(instance.date_of_birth.year) if instance.date_of_birth else None

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        for field in ['race', 'sex', 'ethnicity']:
            rep[field] = 'UN' if not rep.get(field) else rep[field]
        return rep


class PatientSerializer(serializers.ModelSerializer):
    year_of_birth = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ['id', 'patient_id', 'year_of_birth', 'sex', 'race', 'ethnicity']

    def get_year_of_birth(self, instance):
        age = calculate_age(instance.date_of_birth)
        if age is None:
            return None
        if age > 89:
            max_year_of_birth = date.today().year - 89
            return str(max_year_of_birth)
        return str(instance.date_of_birth.year) if instance.date_of_birth else None

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        for field in ['race', 'sex', 'ethnicity']:
            rep[field] = 'UN' if not rep.get(field) else rep[field]
        return rep


class MultiModalDataPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiModalDataPath
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
    


class EncounterSimCenterSerializer(serializers.ModelSerializer):
    encounter_source = serializers.StringRelatedField()
    department = serializers.StringRelatedField()
    patient_id = serializers.SerializerMethodField()
    provider_id = serializers.SerializerMethodField()
    multi_modal_data_id = serializers.SerializerMethodField()

    class Meta:
        model = EncounterSimCenter
        fields = [
            'id', 'provider_id', 'patient_id', 'encounter_source', 'department',
            'multi_modal_data_id', 'encounter_date_and_time', 'is_deidentified', 'is_restricted'
        ]

    def get_patient_id(self, obj):
        return obj.patient.id if obj.patient else None

    def get_provider_id(self, obj):
        return obj.provider.id if obj.provider else None
    
    def get_multi_modal_data_id(self, obj):
        return obj.multi_modal_data.id if obj.multi_modal_data else None


class EncounterRIASSerializer(serializers.ModelSerializer):
    encounter_source = serializers.StringRelatedField()
    department = serializers.StringRelatedField()
    patient_id = serializers.SerializerMethodField()
    provider_id = serializers.SerializerMethodField()
    multi_modal_data_id = serializers.SerializerMethodField()

    class Meta:
        model = EncounterRIAS
        fields = [
            'id', 'provider_id', 'patient_id', 'encounter_source', 'department',
            'multi_modal_data_id', 'is_deidentified', 'is_restricted'
        ]

    def get_patient_id(self, obj):
        return obj.patient.id if obj.patient else None

    def get_provider_id(self, obj):
        return obj.provider.id if obj.provider else None
    
    def get_multi_modal_data_id(self, obj):
        return obj.multi_modal_data.id if obj.multi_modal_data else None
