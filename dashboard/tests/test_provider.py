import os
import csv
from django.test import TestCase
from dashboard.models import Provider
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import IntegrityError
from unittest.mock import patch
import datetime


class ProviderModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.results = []  # Store test results here

    def setUp(self):
        self.provider = Provider.objects.create(
            provider_id=1,
            first_name='John',
            last_name='Doe',
            date_of_birth=None,
            sex='M',
            race='W',
            ethnicity='NH'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        csv_path = os.path.join(os.path.expanduser('~'), 'unit_tests', 'provider_results.csv')
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)

        # Write results to CSV
        with open(csv_path, 'w', newline='') as csvfile:
            fieldnames = ['test_number', 'test_name', 'result', 'input', 'expected', 'actual']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in sorted(cls.results, key=lambda x: int(x['test_number'])):
                writer.writerow(result)

    def append_result(self, test_number, test_name, result, input_data, expected, actual):
        self.__class__.results.append({
            'test_number': test_number,
            'test_name': test_name,
            'result': result,
            'input': input_data,
            'expected': expected,
            'actual': actual
        })

    # General tests

    def test_provider_creation(self, result='PASS', test_number=1):
        try:
            self.assertEqual(Provider.objects.count(), 1)
            self.assertEqual(self.provider.provider_id, 1)
            self.assertEqual(self.provider.first_name, 'John')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_provider_creation', result, 'Provider.objects.count(), self.provider.provider_id, self.provider.first_name', '1, 1, John', f'{Provider.objects.count()}, {self.provider.provider_id}, {self.provider.first_name}')


    def test_str_method(self, result='PASS', test_number=2):
        try:
            self.assertEqual(str(self.provider), 'PR1')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_str_method', result, 'str(self.provider)', 'PR1', str(self.provider))


    def test_provider_creation_with_minimal_data(self, result='PASS', test_number=3):
        try:
            provider = Provider.objects.create(provider_id=5, first_name='Alex', last_name='Johnson')
            self.assertEqual(provider.first_name, 'Alex')
            self.assertEqual(provider.last_name, 'Johnson')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_provider_creation_with_minimal_data', result, "Provider.objects.create(provider_id=5, first_name='Alex', last_name='Johnson')", 'Alex, Johnson', f'{provider.first_name}, {provider.last_name}')
    
    # ID tests

    def test_provider_id_uniqueness(self, result='PASS', test_number=4):
        try:
            Provider.objects.create(provider_id=1)
            result = 'FAIL: No IntegrityError raised'
        except IntegrityError:
            result = 'PASS'
            actual = "IntegrityError"
        except Exception as e:
            result = f'FAIL: Unexpected error {e}'
        self.append_result(test_number, 'test_provider_id_uniqueness', result, 'Duplicate provider_id creation', 'IntegrityError', actual)


    def test_provider_id_auto_increment(self, result='PASS', test_number=5):
        try:
            provider1 = Provider.objects.create(provider_id=10)
            provider2 = Provider.objects.create(provider_id=11)
            self.assertEqual(provider2.provider_id, provider1.provider_id + 1)
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_provider_id_auto_increment', result, 'provider_id auto-increment behavior', '11', str(provider2.provider_id))


    def test_provider_id_0(self, result='PASS', test_number=6):
        try:
            provider_zero = Provider.objects.create(provider_id=0)
            self.assertEqual(provider_zero.provider_id, 0)
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_provider_id_0', result, 'Provider.objects.create(provider_id=0)', '0', str(provider_zero.provider_id))


    def test_provider_id_max_value(self, result='PASS', test_number=7):
        try:
            max_value_provider = Provider.objects.create(provider_id=4294967295)
            self.assertEqual(max_value_provider.provider_id, 4294967295)
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_provider_id_max_value', result, 'Maximum provider_id value test', '4294967295', str(max_value_provider.provider_id))


    def test_provider_negative_id(self, result='PASS', test_number=8):
        provider = None
        try:
            provider = Provider.objects.create(provider_id=-1)
            result = f'FAIL: Negative provider_id accepted, provider_id={provider.provider_id}'
        except IntegrityError as e:
            result = 'PASS'
        except Exception as e:
            result = 'PASS'
        self.append_result(test_number, 'test_provider_negative_id', result, 'Provider.objects.create(provider_id=-1)', 'IntegrityError', f'{provider.provider_id}' if provider else 'IntegrityError')


    def test_provider_id_str_format_with_large_id(self, result='PASS', test_number=9):
        try:
            provider = Provider.objects.create(provider_id=999999999)
            self.assertEqual(str(provider), 'PR999999999')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_provider_id_str_format_with_large_id', result, 'str(provider) with large id', 'PR999999999', str(provider))


    def test_provider_id_blank_provider_creation(self, result='PASS', test_number=10):
        provider = Provider(provider_id="")
        try:
            provider.full_clean()
            result = 'FAIL: No ValidationError raised'
        except ValidationError as e:
            result = 'PASS'
        self.append_result(test_number, 'test_provider_id_blank_provider_creation', result, 'Provider(provider_id="").full_clean()', 'ValidationError', 'N/A')

    # First name tests

    def test_first_name_max_length(self, result='PASS', test_number=11):
        try:
            max_length = Provider._meta.get_field('first_name').max_length
            self.assertEqual(max_length, 255)  # Example expected value
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_first_name_max_length', result, "Provider._meta.get_field('first_name').max_length", '255', max_length)


    def test_provider_update_first_name(self, result='PASS', test_number=12):
        try:
            self.provider.first_name = 'Jane'
            self.provider.save()
            self.provider.refresh_from_db()
            self.assertEqual(self.provider.first_name, 'Jane')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_provider_update_first_name', result, 'Updating first_name', 'Jane', self.provider.first_name)


    def test_first_name_empty_string(self, result='PASS', test_number=13):
        try:
            provider = Provider.objects.create(provider_id=89, first_name='', last_name='Doe')
            self.assertEqual(provider.first_name, '')  # Should allow empty first name
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_first_name_empty_string', result, "Provider.objects.create(provider_id=89, first_name='', last_name='Doe')", '', provider.first_name)


    def test_first_name_max_length_boundary(self, result='PASS', test_number=14):
        try:
            long_name = 'A' * 255  # First name of length 255
            provider = Provider.objects.create(provider_id=27, first_name=long_name, last_name='Smith')
            self.assertEqual(provider.first_name, long_name)
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_first_name_max_length_boundary', result, 'Max length first name (255)', 'A' * 255, provider.first_name)


    def test_first_name_with_spaces(self, result='PASS', test_number=15):
        try:
            provider = Provider.objects.create(provider_id=3, first_name='  John ', last_name='Doe')
            self.assertEqual(provider.first_name, '  John ')  # Leading/trailing spaces should not be trimmed automatically
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_first_name_with_spaces', result, 'First name with spaces', '  John ', provider.first_name)


    def test_first_name_only_space(self, result='FAIL', test_number=16):
        try:
            provider = Provider.objects.create(provider_id=4, first_name=' ', last_name='Doe')
        except IntegrityError:
            result = 'PASS'
        self.append_result(test_number, 'test_first_name_only_space', result, "Provider.objects.create(provider_id=4, first_name=' ', last_name='Doe')", ' ', 'N/A')


    def test_first_name_special_characters(self, result='PASS', test_number=17):
        try:
            special_name = '@$%^&*()'
            provider = Provider.objects.create(provider_id=5, first_name=special_name, last_name='Jones')
            self.assertEqual(provider.first_name, special_name)  # Special characters should be allowed
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_first_name_special_characters', result, 'First name with special characters', '@$%^&*()', provider.first_name)

    # Last name tests

    def test_last_name_max_length(self, result='PASS', test_number=18):
        try:
            max_length = Provider._meta.get_field('last_name').max_length
            self.assertEqual(max_length, 255)
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_last_name_max_length', result, 'Max length of last_name', '255', max_length)

    
    def test_provider_update_last_name(self, result='PASS', test_number=19):
        try:
            self.provider.last_name = 'Doe-Smith'
            self.provider.save()
            self.provider.refresh_from_db()
            self.assertEqual(self.provider.last_name, 'Doe-Smith')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_provider_update_last_name', result, 'Updating last_name', 'Doe-Smith', self.provider.last_name)


    def test_last_name_empty_string(self, result='PASS', test_number=20):
        try:
            provider = Provider.objects.create(provider_id=12345, last_name='')
            self.assertEqual(provider.last_name, '')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_last_name_empty_string', result, 'Last name as empty string', '', provider.last_name)


    def test_last_name_with_special_characters(self, result='PASS', test_number=21):
        try:
            provider = Provider.objects.create(provider_id=12346, last_name='O\'Connor-Smith')
            self.assertEqual(provider.last_name, 'O\'Connor-Smith')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_last_name_with_special_characters', result, 'Last name with special characters', 'O\'Connor-Smith', provider.last_name)


    def test_last_name_minimal_length(self, result='PASS', test_number=22):
        try:
            provider = Provider.objects.create(provider_id=12347, last_name='A')
            self.assertEqual(provider.last_name, 'A')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_last_name_minimal_length', result, "last_name='A'", 'A', provider.last_name)


    def test_last_name_retrieval_case_insensitive(self, result='PASS', test_number=23):
        try:
            provider = Provider.objects.create(provider_id=12348, last_name='dOe')
            retrieved_provider = Provider.objects.get(provider_id=12348)
            self.assertEqual(retrieved_provider.last_name, 'dOe')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_last_name_retrieval_case_insensitive', result, "last_name='dOe'", 'dOe', retrieved_provider.last_name)


    def test_last_name_with_numeric_characters(self, result='PASS', test_number=24):
        try:
            provider = Provider.objects.create(provider_id=12350, last_name='Smith123')
            self.assertEqual(provider.last_name, 'Smith123')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_last_name_with_numeric_characters', result, "last_name='Smith123'", 'Smith123', provider.last_name)
    
    # DOB tests

    def test_null_and_blank_date_of_birth(self, result='PASS', test_number=25):
        try:
            self.assertIsNone(self.provider.date_of_birth)
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_null_and_blank_date_of_birth', result, 'self.provider.date_of_birth', '', self.provider.date_of_birth)


    def test_date_of_birth_format(self, result='PASS', test_number=26):
        try:
            provider = Provider.objects.create(provider_id=1001, first_name="John", last_name="Doe", date_of_birth="1990-01-01")
            self.assertEqual(str(provider.date_of_birth), '1990-01-01')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_date_of_birth_format', result, 'date_of_birth="1990-01-01"', '1990-01-01', str(provider.date_of_birth))


    def test_invalid_date_of_birth(self, result='PASS', test_number=27):
        try:
            with self.assertRaises(ValidationError):
                provider = Provider.objects.create(provider_id=1002, first_name="Jane", last_name="Smith", date_of_birth="invalid-date")
            actual = 'ValidationError'
        except AssertionError as e:
            result = f'FAIL: {e}'
            actual = 'Unexpected Error'
        except ValidationError as e:
            actual = str(e) 
        self.append_result(test_number, 'test_invalid_date_of_birth', result, 'date_of_birth="invalid-date"', 'ValidationError', actual)


    def test_future_date_of_birth(self, result='PASS', test_number=28):
        try:
            future_date = datetime.date.today() + datetime.timedelta(days=1)
            with self.assertRaises(ValidationError):
                provider = Provider(provider_id=1003, first_name="Alice", last_name="Johnson", date_of_birth=future_date)
                provider.full_clean()  # This triggers the validation
            actual = 'ValidationError'
        except AssertionError:
            result = 'FAIL'
            actual = 'No ValidationError'
        self.append_result(test_number, 'test_future_date_of_birth', result, f'date_of_birth={future_date}', 'ValidationError', actual)


    def test_maximum_age(self, result='PASS', test_number=29):
        try:
            unrealistic_birth_date = datetime.date.today() - datetime.timedelta(days=140 * 365)  # 140 years ago
            provider = Provider.objects.create(provider_id=1004, first_name="Bob", last_name="Williams", date_of_birth=unrealistic_birth_date)
            self.assertTrue(provider.date_of_birth < datetime.date.today())
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_maximum_age', result, 'Unrealistically old date_of_birth', 'True', provider.date_of_birth < datetime.date.today())

    # Sex tests

    def test_sex_choices(self, result='PASS', test_number=30):
        try:
            choices = [choice[0] for choice in Provider._meta.get_field('sex').choices]
            self.assertIn('M', choices)
            self.assertIn('F', choices)
            self.assertIn('UN', choices)
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_sex_choices', result, 'Allowed choices for sex', "['M', 'F', 'UN']", str(choices))


    def test_sex_field_blank_value(self, result='PASS', test_number=31):
        try:
            provider = Provider.objects.create(provider_id=52, sex="")
            self.assertEqual(provider.sex, "")  # Ensure the field is blank if no value is given
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_sex_field_blank_value', result, 'Sex field when blank', '', provider.sex)


    def test_sex_field_unique_value(self, result='PASS', test_number=32):
        try:
            provider_1 = Provider.objects.create(provider_id=37, sex="M")
            provider_2 = Provider.objects.create(provider_id=64, sex="F")
            self.assertNotEqual(provider_1.sex, provider_2.sex)  # Ensure that the sex values are correctly assigned and can be different
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_sex_field_unique_value', result, 'Different providers with different sex values', 'M != F', f'{provider_1.sex} != {provider_2.sex}')


    def test_sex_field_value_inconsistency(self, result='PASS', test_number=33):
        try:
            provider_1 = Provider.objects.create(provider_id=95, sex="M")
            provider_2 = Provider.objects.create(provider_id=96, sex="F")
            provider_1.sex = "F"  # Change value to test if update works as expected
            provider_1.save()
            self.assertEqual(provider_1.sex, "F")  # Check if the update works
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_sex_field_value_inconsistency', result, 'Sex field value change consistency', 'F', provider_1.sex)


    def test_sex_invalid_value_handling(self, result='PASS', test_number=34):
        exception_message = ''
        try:
            provider = Provider.objects.create(provider_id=87, sex="X")
            provider.full_clean()
            self.fail("ValidationError not raised for invalid sex value")
        except ValidationError as e:
            self.assertIn('sex', str(e))
            exception_message = str(e)
        except AssertionError as e:
            result = f'FAIL: {e}'
            exception_message = str(e)
        self.append_result(test_number, 'test_sex_invalid_value_handling', result, 'Sex field invalid value handling', 'ValidationError', exception_message)


    # Race tests

    def test_race_field_not_null(self, result='PASS', test_number=35):
        try:
            field = Provider._meta.get_field('race')
            self.assertFalse(field.null)
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_race_field_not_null', result, 'Field null constraint for race', 'False', field.null)


    def test_race_field_max_length(self, result='PASS', test_number=36):
        try:
            field = Provider._meta.get_field('race')
            self.assertEqual(field.max_length, 5)
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_race_field_max_length', result, 'Max length of race field', '5', field.max_length)


    def test_race_field_invalid_choice(self, result='PASS', test_number=37):
        try:
            invalid_choice = 'XYZ'
            provider = Provider.objects.create(provider_id=157, race=invalid_choice)
            provider.full_clean()  # This will raise a ValidationError if the choice is invalid
        except ValidationError as e:
            actual = "ValidationError"
        except Exception as e:
            result = f'FAIL: Unexpected error {e}'
        self.append_result(test_number, 'test_race_field_invalid_choice', result, 'race=XYZ', 'ValidationError', actual)


    def test_race_field_default_value(self, result='PASS', test_number=38):
        try:
            provider = Provider.objects.create(provider_id=158)
            self.assertEqual(provider.race, '')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_race_field_default_value', result, 'Default race value when not provided', "''", provider.race)


    def test_race_field_empty_string(self, result='PASS', test_number=39):
        try:
            provider = Provider.objects.create(provider_id=159, race='')
            provider.full_clean()  # Should pass since race can be empty
        except ValidationError as e:
            result = f'FAIL: Unexpected ValidationError {e}'
        except Exception as e:
            result = f'FAIL: Unexpected error {e}'
        self.append_result(test_number, 'test_race_field_empty_string', result, 'Race field can be empty string', 'No ValidationError', result)


    def test_race_field_all_choices(self, result='PASS', test_number=40):
        try:
            for e, choice in enumerate(['AI', 'A', 'NHPI', 'B', 'W', 'M', 'UN']):
                provider = Provider.objects.create(provider_id=e+293, race=choice)
                provider.full_clean()  # Ensuring each race choice is valid and passes full_clean
            result = 'PASS: All race choices are accepted'
        except ValidationError as e:
            result = f'FAIL: ValidationError raised {e}'
        except Exception as e:
            result = f'FAIL: Unexpected error {e}'
        self.append_result(test_number, 'test_race_field_all_choices', result, 'Test all possible race choices', 'No ValidationError', result)


    def test_race_field_not_blank_for_non_empty_value(self, result='PASS', test_number=41):
        try:
            provider = Provider.objects.create(provider_id=555, race='B')
            self.assertFalse(provider.race == '')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_race_field_not_blank_for_non_empty_value', result, 'Non-empty race should not be blank', 'False', provider.race == '')


    def test_race_field_edge_case(self, result='PASS', test_number=42):
        try:
            provider = Provider.objects.create(provider_id=675, race='AI')
            provider.save()
            self.assertEqual(provider.race, 'AI')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_race_field_edge_case', result, 'Test edge case race value', "AI", provider.race)

    # Ethnicity tests

    def test_ethnicity_field_not_null(self, result='PASS', test_number=43):
        try:
            field = Provider._meta.get_field('ethnicity')
            self.assertFalse(field.null)
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_ethnicity_field_not_null', result, 'Field null constraint for ethnicity', 'False', field.null)


    def test_ethnicity_field_max_length(self, result='PASS', test_number=44):
        try:
            field = Provider._meta.get_field('ethnicity')
            self.assertEqual(field.max_length, 5)
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_ethnicity_field_max_length', result, 'Max length of ethnicity field', '5', field.max_length)

    # Timestamp tests

    def test_timestamp_auto_now_add(self, result='PASS', test_number=45):
        try:
            field = Provider._meta.get_field('timestamp')
            self.assertTrue(field.auto_now_add)
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_timestamp_auto_now_add', result, 'Auto now add for timestamp field', 'True', field.auto_now_add)


    def test_timestamp_not_updated_on_save(self, result='PASS', test_number=46):
        try:
            obj = Provider.objects.create(provider_id=777)
            original_timestamp = obj.timestamp
            obj.save()  # Save the object again
            self.assertEqual(obj.timestamp, original_timestamp)
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_timestamp_not_updated_on_save', result, 'Timestamp field should not be updated after save', 'True', obj.timestamp == original_timestamp)


    def test_timestamp_is_valid_datetime(self, result='PASS', test_number=47):
        try:
            obj = Provider.objects.create(provider_id=778)
            self.assertIsInstance(obj.timestamp, timezone.datetime)
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_timestamp_is_valid_datetime', result, 'Timestamp should be a valid datetime object', 'True', isinstance(obj.timestamp, timezone.datetime))


    def test_timestamp_auto_now_add_default(self, result='PASS', test_number=48):
        try:
            obj = Provider.objects.create(provider_id=779)
            self.assertIsNotNone(obj.timestamp)
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_timestamp_auto_now_add_default', result, 'Timestamp field should be automatically populated on creation', 'True', obj.timestamp is not None)
