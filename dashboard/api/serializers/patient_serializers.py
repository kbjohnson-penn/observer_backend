from rest_framework import serializers
from datetime import date
from dashboard.models import Patient
from dashboard.utils import calculate_age


class PublicPatientSerializer(serializers.ModelSerializer):
    year_of_birth = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ['id', 'year_of_birth',
                  'sex', 'race', 'ethnicity']

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
            rep[field] = rep.get(field, 'UN')
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
            return str(max_year_of_birth)
        return str(instance.date_of_birth.year) if instance.date_of_birth else None

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        for field in ['race', 'sex', 'ethnicity']:
            rep[field] = rep.get(field, 'UN')
        return rep
