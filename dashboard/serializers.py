from rest_framework import serializers
from datetime import date
from dateutil.relativedelta import relativedelta
from .models import Patient, Provider, Department, MultiModalDataPath, Encounter, EncounterSource, EncounterSimCenter, EncounterRIAS

BOOLEAN_CHOICES = {
    True: 'Yes',
    False: 'No',
}


def calculate_age(date_of_birth):
    if date_of_birth is None:
        return None  # or a default value, e.g., 0 or 'Unknown'
    today = date.today()
    age = relativedelta(today, date_of_birth).years
    return age


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
        fields = ['id', 'provider_id', 'year_of_birth',
                  'sex', 'race', 'ethnicity']

    def get_year_of_birth(self, instance):
        age = calculate_age(instance.date_of_birth)
        if age is None:
            return None
        if age > 89:
            max_year_of_birth = date.today().year - 89
            return max_year_of_birth
        return instance.date_of_birth.year

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['race'] = 'UN' if rep.get('race') == '' else rep['race']
        rep['sex'] = 'UN' if rep.get('sex') == '' else rep['sex']
        rep['ethnicity'] = 'UN' if rep.get(
            'ethnicity') == '' else rep['ethnicity']
        return rep


class PatientSerializer(serializers.ModelSerializer):
    year_of_birth = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ['id', 'patient_id', 'year_of_birth',
                  'sex', 'race', 'ethnicity']

    def get_year_of_birth(self, instance):
        age = calculate_age(instance.date_of_birth)
        if age is None:
            return None
        if age > 89:
            max_year_of_birth = date.today().year - 89
            return max_year_of_birth
        return instance.date_of_birth.year

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['race'] = 'UN' if rep.get('race') == '' else rep['race']
        rep['sex'] = 'UN' if rep.get('sex') == '' else rep['sex']
        rep['ethnicity'] = 'UN' if rep.get(
            'ethnicity') == '' else rep['ethnicity']
        return rep


class MultiModalDataPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiModalDataPath
        fields = ['id', 'provider_view', 'patient_view', 'room_view',
                  'audio', 'transcript', 'patient_survey', 'provider_survey', 'patient_annotation', 'provider_annotation', 'rias_transcript', 'rias_codes']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        for field in ['provider_view', 'patient_view', 'room_view', 'audio', 'transcript', 'patient_survey', 'provider_survey', 'patient_annotation', 'provider_annotation', 'rias_transcript', 'rias_codes']:
            rep[field] = bool(rep[field])
        return rep


class EncounterSerializer(serializers.ModelSerializer):
    encounter_source = serializers.StringRelatedField()
    department = serializers.StringRelatedField()
    patient_id = serializers.SerializerMethodField()
    provider_id = serializers.SerializerMethodField()
    multi_modal_data_id = serializers.SerializerMethodField()

    class Meta:
        model = Encounter
        fields = ['id', 'provider_id', 'patient_id', 'encounter_source', 'department', 'multi_modal_data_id',
                  'encounter_date_and_time', 'patient_satisfaction', 'provider_satisfaction', 'is_deidentified', 'is_restricted']

    def get_patient_id(self, obj):
        return obj.patient.id

    def get_provider_id(self, obj):
        return obj.provider.id

    def get_multi_modal_data_id(self, obj):
        return obj.multi_modal_data.id


class EncounterSimCenterSerializer(serializers.ModelSerializer):
    encounter_source = serializers.StringRelatedField()
    department = serializers.StringRelatedField()
    patient_id = serializers.SerializerMethodField()
    provider_id = serializers.SerializerMethodField()
    multi_modal_data_id = serializers.SerializerMethodField()

    class Meta:
        model = EncounterSimCenter
        fields = ['id', 'provider_id', 'patient_id', 'encounter_source', 'department', 'multi_modal_data_id',
                  'encounter_date_and_time', 'is_deidentified', 'is_restricted']

    def get_patient_id(self, obj):
        return obj.patient.id

    def get_provider_id(self, obj):
        return obj.provider.id

    def get_multi_modal_data_id(self, obj):
        return obj.multi_modal_data.id


class EncounterRIASSerializer(serializers.ModelSerializer):
    encounter_source = serializers.StringRelatedField()
    department = serializers.StringRelatedField()
    patient_id = serializers.SerializerMethodField()
    provider_id = serializers.SerializerMethodField()
    multi_modal_data_id = serializers.SerializerMethodField()

    class Meta:
        model = EncounterRIAS
        fields = ['id', 'provider_id', 'patient_id', 'encounter_source', 'department', 'multi_modal_data_id',
                  'is_deidentified', 'is_restricted']

    def get_patient_id(self, obj):
        return obj.patient.id

    def get_provider_id(self, obj):
        return obj.provider.id

    def get_multi_modal_data_id(self, obj):
        return obj.multi_modal_data.id
