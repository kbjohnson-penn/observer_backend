from django.test import TestCase
from dashboard.models import Patient
from django.core.exceptions import ValidationError


class PatientModelTest(TestCase):
    def setUp(self):
        self.patient_data = {'patient_id': '125',
                             'first_name': 'John', 'last_name': 'Doe'}
        self.patient = Patient.objects.create(**self.patient_data)

    def test_patient_creation(self):
        self.assertEqual(Patient.objects.count(), 1)
        self.assertEqual(self.patient.patient_id, 'P125')
        self.assertEqual(self.patient.first_name, 'John')
        self.assertEqual(self.patient.last_name, 'Doe')

    def test_patient_id_validation(self):
        with self.assertRaises(ValidationError):
            Patient.objects.create(
                patient_id='abc', first_name='John', last_name='Doe')

    def test_patient_id_cleaning(self):
        self.assertEqual(self.patient.patient_id, 'P125')

    def test_patient_id_uniqueness(self):
        with self.assertRaises(ValidationError):
            Patient.objects.create(**self.patient_data)

    def test_patient_str(self):
        self.assertEqual(str(self.patient), 'P125')
