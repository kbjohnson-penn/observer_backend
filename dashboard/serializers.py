from rest_framework import serializers
from .models import Patient, Provider, Department, MultiModalDataPath, Encounter


class GraphPatientSerializer(serializers.Serializer):
    race = serializers.CharField()
    ethnicity = serializers.CharField()
    date_of_birth = serializers.DateField()
    sex = serializers.CharField()


class GraphProviderSerializer(serializers.Serializer):
    race = serializers.CharField()
    ethnicity = serializers.CharField()
    date_of_birth = serializers.DateField()
    sex = serializers.CharField()


class GraphDepartmentSerializer(serializers.Serializer):
    name = serializers.CharField()


class GraphEncounterSerializer(serializers.Serializer):
    case_id = serializers.CharField()
    encounter_date = serializers.DateField()


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class MultiModalDataPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiModalDataPath
        fields = '__all__'


class EncounterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Encounter
        fields = '__all__'
