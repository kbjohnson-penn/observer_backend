from clinical.models import Patient
from .base_serializers import PersonSerializer


class PublicPatientSerializer(PersonSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'year_of_birth', 'sex', 'race', 'ethnicity']


class PatientSerializer(PersonSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'patient_id', 'year_of_birth', 'sex', 'race', 'ethnicity']
