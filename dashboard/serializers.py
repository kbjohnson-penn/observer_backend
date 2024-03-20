from rest_framework import serializers
from .models import Patient, Provider, Department, MultiModalDataPath, Encounter

BOOLEAN_CHOICES = {
    True: 'Yes',
    False: 'No',
}

RACIAL_CATEGORIES = {
    'AI': 'American Indian or Alaska Native',
    'A': 'Asian',
    'NHPI': 'Native Hawaiian or Other Pacific Islander',
    'B': 'Black or African American',
    'W': 'White',
    'M': 'More than One Race',
    'UN': 'Unknown or Not Reported',
}

ETHNIC_CATEGORIES = {
    'H': 'Hispanic or Latino',
    'NH': 'Not Hispanic or Latino',
    'UN': 'Unknown or Not Reported Ethnicity',
}

SEX_CATEGORIES = {
    'M': 'Male',
    'F': 'Female',
    'UN': 'Unknown or Not Reported'
}


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['patient_id', 'date_of_birth', 'sex', 'race', 'ethnicity']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['race'] = RACIAL_CATEGORIES[rep['race']]
        rep['ethnicity'] = ETHNIC_CATEGORIES[rep['ethnicity']]
        rep['sex'] = SEX_CATEGORIES[rep['sex']]
        return rep


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ['provider_id', 'date_of_birth', 'sex', 'race', 'ethnicity']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['race'] = RACIAL_CATEGORIES[rep['race']]
        rep['ethnicity'] = ETHNIC_CATEGORIES[rep['ethnicity']]
        rep['sex'] = SEX_CATEGORIES[rep['sex']]
        return rep


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['name']


class MultiModalDataPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiModalDataPath
        fields = ['multi_modal_data_id', 'provider_view', 'patient_view', 'room_view',
                  'audio', 'transcript', 'patient_survey', 'provider_survey']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        for field in ['provider_view', 'patient_view', 'room_view', 'audio', 'transcript', 'patient_survey', 'provider_survey']:
            rep[field] = bool(rep[field])
        return rep


class EncounterSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField()
    patient = serializers.StringRelatedField()
    provider = serializers.StringRelatedField()
    multi_modal_data = serializers.StringRelatedField()

    class Meta:
        model = Encounter
        fields = ['case_id', 'provider', 'patient', 'department', 'multi_modal_data',
                  'encounter_date_and_time', 'patient_satisfaction', 'provider_satisfaction', 'is_deidentified', 'is_restricted']
