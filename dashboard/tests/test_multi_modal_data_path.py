from django.test import TestCase
from dashboard.models import MultiModalDataPath
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


class MultiModalDataPathModelTest(TestCase):
    def setUp(self):
        self.multi_modal_data_path = MultiModalDataPath.objects.create(
            multi_modal_data_id='125',
            provider_view='http://example.com/provider_view',
            patient_view='http://example.com/patient_view',
            room_view='http://example.com/room_view',
            audio='http://example.com/audio',
            transcript='http://example.com/transcript',
            patient_survey='http://example.com/patient_survey',
            provider_survey='http://example.com/provider_survey',
            rias_transcript='http://example.com/rias_transcript',
            rias_codes='http://example.com/rias_codes'
        )

    def test_multi_modal_data_path_creation(self):
        self.assertEqual(MultiModalDataPath.objects.count(), 1)
        self.assertEqual(
            self.multi_modal_data_path.multi_modal_data_id, 'MMD125')
        self.assertEqual(self.multi_modal_data_path.provider_view,
                         'http://example.com/provider_view')
        self.assertEqual(self.multi_modal_data_path.patient_view,
                         'http://example.com/patient_view')
        self.assertEqual(self.multi_modal_data_path.room_view,
                         'http://example.com/room_view')
        self.assertEqual(self.multi_modal_data_path.audio,
                         'http://example.com/audio')
        self.assertEqual(self.multi_modal_data_path.transcript,
                         'http://example.com/transcript')
        self.assertEqual(self.multi_modal_data_path.patient_survey,
                         'http://example.com/patient_survey')
        self.assertEqual(self.multi_modal_data_path.provider_survey,
                         'http://example.com/provider_survey')
        self.assertEqual(self.multi_modal_data_path.rias_transcript,
                         'http://example.com/rias_transcript')
        self.assertEqual(self.multi_modal_data_path.rias_codes,
                         'http://example.com/rias_codes')

    def test_multi_modal_data_path_str(self):
        self.assertEqual(str(self.multi_modal_data_path), 'MMD125')

    def test_multi_modal_data_path_uniqueness(self):
        with self.assertRaises(Exception):
            MultiModalDataPath.objects.create(multi_modal_data_id='125')

    def test_multi_modal_data_path_id_validation(self):
        with self.assertRaises(ValidationError):
            MultiModalDataPath.objects.create(multi_modal_data_id='abc')

    def test_multi_modal_data_path_invalid_url(self):
        invalid_url = 'invalid_url'
        with self.assertRaises(ValidationError):
            validate = URLValidator()
            url_fields = ['provider_view', 'patient_view', 'room_view', 'audio', 'transcript',
                          'patient_survey', 'provider_survey', 'rias_transcript', 'rias_codes']
            for field in url_fields:
                data = {field: invalid_url}
                data.update(
                    {f: 'http://example.com' for f in url_fields if f != field})
                data['multi_modal_data_id'] = 'MMD125'
                multi_modal_data_path = MultiModalDataPath.objects.create(
                    **data)
                validate(multi_modal_data_path.__dict__[field])
