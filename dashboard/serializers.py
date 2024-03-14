from rest_framework import serializers
from .models import Patient, Provider, Department, MultiModalDataPath, Encounter


# class GraphPatientSerializer(serializers.Serializer):
#     race = serializers.CharField()
#     ethnicity = serializers.CharField()
#     date_of_birth = serializers.DateField()
#     sex = serializers.CharField()


# class GraphProviderSerializer(serializers.Serializer):
#     race = serializers.CharField()
#     ethnicity = serializers.CharField()
#     date_of_birth = serializers.DateField()
#     sex = serializers.CharField()


# class GraphDepartmentSerializer(serializers.Serializer):
#     name = serializers.CharField()


# class GraphEncounterSerializer(serializers.Serializer):
#     case_id = serializers.CharField()
#     encounter_date = serializers.DateField()


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['patient_id', 'date_of_birth', 'sex', 'race', 'ethnicity']


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ['provider_id', 'date_of_birth', 'sex', 'race', 'ethnicity']


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class MultiModalDataPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiModalDataPath
        fields = ['multi_modal_data_id']


class EncounterSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField()
    patient = serializers.StringRelatedField()
    provider = serializers.StringRelatedField()
    multi_modal_data = serializers.StringRelatedField()

    class Meta:
        model = Encounter
        fields = ['case_id', 'provider', 'patient', 'department', 'multi_modal_data',
                  'encounter_date', 'encounter_time', 'overall_satisfaction', 'is_deidentified', 'is_restricted', 'timestamp']
