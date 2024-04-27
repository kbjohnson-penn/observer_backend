from django.test import TestCase
from dashboard.models import Provider
from django.core.exceptions import ValidationError


class ProviderModelTest(TestCase):
    def setUp(self):
        self.provider_data = {'provider_id': '125',
                              'first_name': 'John', 'last_name': 'Doe'}
        self.provider = Provider.objects.create(**self.provider_data)

    def test_provider_creation(self):
        self.assertEqual(Provider.objects.count(), 1)
        self.assertEqual(self.provider.provider_id, 'PR125')
        self.assertEqual(self.provider.first_name, 'John')
        self.assertEqual(self.provider.last_name, 'Doe')

    def test_provider_id_validation(self):
        with self.assertRaises(ValidationError):
            Provider.objects.create(
                provider_id='abc', first_name='John', last_name='Doe')

    def test_provider_id_cleaning(self):
        self.assertEqual(self.provider.provider_id, 'PR125')

    def test_provider_id_uniqueness(self):
        with self.assertRaises(ValidationError):
            Provider.objects.create(**self.provider_data)

    def test_provider_str(self):
        self.assertEqual(str(self.provider), 'PR125')
