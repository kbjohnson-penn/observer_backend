from django.test import TestCase
from dashboard.models import EncounterSource


class EncounterSourceModelTest(TestCase):
    def setUp(self):
        self.encounter_source = EncounterSource.objects.create(
            name='Test Source')

    def test_encounter_source_creation(self):
        self.assertEqual(EncounterSource.objects.count(), 1)
        self.assertEqual(self.encounter_source.name, 'Test Source')

    def test_encounter_source_str(self):
        self.assertEqual(str(self.encounter_source), 'Test Source')

    def test_encounter_source_uniqueness(self):
        with self.assertRaises(Exception):
            EncounterSource.objects.create(name='Test Source')
