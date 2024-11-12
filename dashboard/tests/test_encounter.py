from django.test import TestCase
from dashboard.models import Patient, Provider, EncounterSource, Department, MultiModalData, Encounter
from django.core.exceptions import ValidationError
from django.utils import timezone


class EncounterModelTest(TestCase):
    def setUp(self):
        self.encounter_source = EncounterSource.objects.create(
            name='Test Source')
        self.department = Department.objects.create(name='Test Department')
        self.provider = Provider.objects.create(
            provider_id='125', first_name='John', last_name='Doe')
        self.patient = Patient.objects.create(
            patient_id='125', first_name='John', last_name='Doe')
        self.encounter = Encounter.objects.create(
            case_id='125',
            encounter_source=self.encounter_source,
            department=self.department,
            provider=self.provider,
            patient=self.patient,

            encounter_date_and_time=timezone.now()  # Use timezone-aware datetime
        )

    def test_encounter_creation(self):
        self.assertEqual(Encounter.objects.count(), 1)
        self.assertEqual(self.encounter.case_id, 'E125')
        self.assertEqual(self.encounter.encounter_source,
                         self.encounter_source)
        self.assertEqual(self.encounter.department, self.department)
        self.assertEqual(self.encounter.provider, self.provider)
        self.assertEqual(self.encounter.patient, self.patient)

    def test_encounter_str(self):
        self.assertEqual(str(self.encounter), 'E125')

    def test_encounter_case_id_uniqueness(self):
        with self.assertRaises(Exception):
            Encounter.objects.create(
                case_id='125',
                encounter_source=self.encounter_source,
                department=self.department,
                provider=self.provider,
                patient=self.patient,

            )

    def test_encounter_case_id_validation(self):
        with self.assertRaises(ValidationError):
            Encounter.objects.create(
                case_id='abc',
                encounter_source=self.encounter_source,
                department=self.department,
                provider=self.provider,
                patient=self.patient,

            )

    def test_encounter_date(self):
        self.assertEqual(
            self.encounter.encounter_date_and_time.date(), timezone.localtime(timezone.now()).date())

    def test_patient_satisfaction(self):
        Encounter.objects.filter(pk=self.encounter.pk).update(
            patient_satisfaction=5)
        self.encounter.refresh_from_db()
        self.assertEqual(self.encounter.patient_satisfaction, 5)

    def test_provider_satisfaction(self):
        Encounter.objects.filter(pk=self.encounter.pk).update(
            provider_satisfaction=5)
        self.encounter.refresh_from_db()
        self.assertEqual(self.encounter.provider_satisfaction, 5)

    def test_encounter_case_id_empty(self):
        with self.assertRaises(ValidationError):
            Encounter.objects.create(
                case_id='',
                encounter_source=self.encounter_source,
                department=self.department,
                provider=self.provider,
                patient=self.patient,

            )

    def test_encounter_case_id_whitespace(self):
        with self.assertRaises(ValidationError):
            Encounter.objects.create(
                case_id='   ',
                encounter_source=self.encounter_source,
                department=self.department,
                provider=self.provider,
                patient=self.patient,

            )

    def test_patient_satisfaction_negative(self):
        with self.assertRaises(ValidationError):
            Encounter.objects.create(
                case_id='126',
                encounter_source=self.encounter_source,
                department=self.department,
                provider=self.provider,
                patient=self.patient,

                patient_satisfaction=-1
            )

    def test_provider_satisfaction_negative(self):
        with self.assertRaises(ValidationError):
            Encounter.objects.create(
                case_id='126',
                encounter_source=self.encounter_source,
                department=self.department,
                provider=self.provider,
                patient=self.patient,

                provider_satisfaction=-1
            )

    def test_encounter_date_future(self):
        future_date = timezone.now() + timezone.timedelta(days=1)
        encounter = Encounter.objects.create(
            case_id='126',
            encounter_source=self.encounter_source,
            department=self.department,
            provider=self.provider,
            patient=self.patient,

            encounter_date_and_time=future_date
        )
        self.assertEqual(
            encounter.encounter_date_and_time.date(), future_date.date())
