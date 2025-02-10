import os
import csv
from django.test import TestCase
from dashboard.models import Department
from unittest.mock import patch


class DepartmentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.results = []  # Store test results here

    def setUp(self):
        self.department = Department.objects.create(name='Test Department')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        csv_path = os.path.join(os.path.expanduser('~'), 'unit_tests', 'test_results.csv')
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


    def test_department_creation(self, result='PASS', test_number=1):
        try:
            self.assertEqual(Department.objects.count(), 1)
            self.assertEqual(self.department.name, 'Test Department')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_creation', result, 'Department.objects.count(), self.department.name', '1, Test Department', f'{Department.objects.count()}, {self.department.name}')


    def test_department_str(self, result='PASS', test_number=2):
        try: 
            self.assertEqual(str(self.department), 'Test Department')
        except AssertionError as e: 
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_str', result, 'str(self.department)', 'Test Department', str(self.department))


    def test_department_name_max_length(self, result='PASS', test_number=3):
        try:
            max_length = self.department._meta.get_field('name').max_length
            self.assertEqual(max_length, 50)
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_max_length', result, 'self.department._meta.get_field("name").max_length', '50', max_length)


    def test_department_name_unique(self, result='PASS', test_number=4):
        try:
            duplicate_department = Department(name='Test Department')
            with self.assertRaises(Exception):
                duplicate_department.save()
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_unique', result, 'duplicate_department.save()', 'Exception', 'Exception' if result == 'PASS' else 'No Exception')


    def test_department_verbose_name(self, result='PASS', test_number=5):
        try:
            verbose_name = self.department._meta.verbose_name
            self.assertEqual(verbose_name, 'Department')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_verbose_name', result, 'self.department._meta.verbose_name', 'Department', verbose_name)


    def test_department_verbose_name_plural(self, result='PASS', test_number=6):
        try:
            verbose_name_plural = self.department._meta.verbose_name_plural
            self.assertEqual(verbose_name_plural, 'Departments')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_verbose_name_plural', result, 'self.department._meta.verbose_name_plural', 'Departments', verbose_name_plural)


    def test_department_name_blank(self, result='PASS', test_number=7):
        try:
            department = Department(name='')
            with self.assertRaises(Exception):
                department.save()
        except AssertionError as e:
            result = f'FAIL: {e}'
        actual = 'Exception' if result == 'PASS' else 'No Exception'
        self.append_result(test_number, 'test_department_name_blank', result, 'Department(name="")', 'Exception', actual)


    def test_department_name_null(self, result='PASS', test_number=8):
        try:
            department = Department(name=None)
            with self.assertRaises(Exception):
                department.save()
        except AssertionError as e:
            result = f'FAIL: {e}'
        actual = 'Exception' if result == 'PASS' else 'No Exception'
        self.append_result(test_number, 'test_department_name_null', result, 'Department(name=None)', 'Exception', actual)


    def test_department_name_case_insensitive_unique(self, result='PASS', test_number=9):
        try:
            department_lower = Department(name='test department')
            with self.assertRaises(Exception):
                department_lower.save()
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_case_insensitive_unique', result, 'Department(name="test department")', 'Exception', 'Exception' if result == 'PASS' else 'No Exception')


    def test_department_name_whitespace(self, result='PASS', test_number=10):
        try:
            department_whitespace = Department(name='   ')
            with self.assertRaises(Exception):
                department_whitespace.save()
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_whitespace', result, 'Department(name="   ")', 'Exception', 'Exception' if result == 'PASS' else 'No Exception')


    def test_department_name_special_characters(self, result='PASS', test_number=11):
        try:
            department_special = Department(name='Test@Department!')
            department_special.save()
            self.assertEqual(department_special.name, 'Test@Department!')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_special_characters', result, 'Department(name="Test@Department!")', 'Test@Department!', department_special.name)


    def test_department_name_length(self, result='PASS', test_number=12):
        try:
            department_long_name = Department(name='A' * 51)
            with self.assertRaises(Exception):
                department_long_name.save()
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_length', result, 'Department(name="A" * 51)', 'Exception', 'Exception' if result == 'PASS' else 'No Exception')


    def test_department_name_trailing_whitespace(self, result='PASS', test_number=13):
        try:
            department_trailing_whitespace = Department(name='Test Department1   ')
            department_trailing_whitespace.save()
            self.assertEqual(department_trailing_whitespace.name, 'Test Department1   ')
        except AssertionError as e:
            result = f'FAIL: {e}'
        except Exception as e:
            result = f'ERROR: {e}'
        finally:
            self.append_result(test_number, 'test_department_name_trailing_whitespace', result, 'Department(name="Test Department   ")', 'Test Department   ', department_trailing_whitespace.name)


    def test_department_name_leading_whitespace(self, result='PASS', test_number=14):
        try:
            department_leading_whitespace = Department(name='   Test Department')
            department_leading_whitespace.save()
            self.assertEqual(department_leading_whitespace.name, '   Test Department')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_leading_whitespace', result, 'Department(name="   Test Department")', '   Test Department', department_leading_whitespace.name)


    def test_department_name_internal_whitespace(self, result='PASS', test_number=15):
        try:
            department_internal_whitespace = Department(name='Test   Department')
            department_internal_whitespace.save()
            self.assertEqual(department_internal_whitespace.name, 'Test   Department')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_internal_whitespace', result, 'Department(name="Test   Department")', 'Test   Department', department_internal_whitespace.name)


    def test_department_name_numeric(self, result='PASS', test_number=16):
        try:
            department_numeric = Department(name='12345')
            department_numeric.save()
            self.assertEqual(department_numeric.name, '12345')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_numeric', result, 'Department(name="12345")', '12345', department_numeric.name)


    def test_department_name_alphanumeric(self, result='PASS', test_number=17):
        try:
            department_alphanumeric = Department(name='Test123')
            department_alphanumeric.save()
            self.assertEqual(department_alphanumeric.name, 'Test123')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_alphanumeric', result,'Department(name="Test123")', 'Test123', department_alphanumeric.name)


    def test_department_name_lowercase(self, result='PASS', test_number=18):
        try:
            department_lowercase = Department(name='testdepartment')
            department_lowercase.save()
            self.assertEqual(department_lowercase.name, 'testdepartment')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_lowercase', result,'Department(name="testdepartment")', 'testdepartment', department_lowercase.name)


    def test_department_name_uppercase(self, result='PASS', test_number=19):
        try:
            department_uppercase = Department(name='TESTDEPARTMENT')
            department_uppercase.save()
            self.assertEqual(department_uppercase.name, 'TESTDEPARTMENT')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_uppercase', result,'Department(name="TESTDEPARTMENT")', 'TESTDEPARTMENT', department_uppercase.name)


    def test_department_name_trim_whitespace(self, result='PASS', test_number=20):
        try:
            department_trimmed = Department(name='  Trimmed Department  '.strip())
            department_trimmed.save()
            self.assertEqual(department_trimmed.name, 'Trimmed Department')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_trim_whitespace', result,'Department(name="  Trimmed Department  ")', 'Trimmed Department', department_trimmed.name)


    def test_department_name_duplicate_different_case(self, result='PASS', test_number=21):
        try:
            Department(name='Department').save()
            with self.assertRaises(Exception):
                Department(name='department').save()
        except Exception as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_duplicate_different_case', result, 'Department(name="Department") and Department(name="department")', 'Exception', 'Exception' if result == 'PASS' else 'No Exception')


    def test_department_name_unicode(self, result='PASS', test_number=22):
        try:
            department_unicode = Department(name='Département')
            department_unicode.save()
            self.assertEqual(department_unicode.name, 'Département')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_unicode', result,'Department(name="Département")', 'Département', department_unicode.name)


    def test_department_name_numeric_with_symbols(self, result='PASS', test_number=23):
        try:
            department_numeric_symbols = Department(name='1234-5678')
            department_numeric_symbols.save()
            self.assertEqual(department_numeric_symbols.name, '1234-5678')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_numeric_with_symbols', result, 'Department(name="1234-5678")', '1234-5678', department_numeric_symbols.name)


    def test_department_name_extremely_long_input(self, result='PASS', test_number=24):
        try:
            department_long_name = Department(name='A' * 1000)
            department_long_name.save()
            result = 'FAIL: Exception not raised'
            actual = department_long_name.name
        except Exception as e:
            actual = str(e)
        self.append_result(test_number, 'test_department_name_extremely_long_input', result,'Department(name="A" * 1000)', 'Exception', actual)


    def test_department_name_mixed_whitespace_symbols(self, result='PASS', test_number=25):
        try:
            department_mixed = Department(name=' Test @Dept # ')
            department_mixed.save()
            self.assertEqual(department_mixed.name, ' Test @Dept # ')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_mixed_whitespace_symbols', result, 'Department(name=" Test @Dept # ")', ' Test @Dept # ', department_mixed.name)

    
    def test_department_name_special_unicode_symbols(self, result='PASS', test_number=26):
        try:
            department_unicode_symbol = Department(name='Dept★')
            department_unicode_symbol.save()
            self.assertEqual(department_unicode_symbol.name, 'Dept★')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_special_unicode_symbols', result, 'Department(name="Dept★")', 'Dept★', department_unicode_symbol.name)


    def test_department_name_empty_space_end(self, result='PASS', test_number=27):
        try:
            department_space_end = Department(name='Department ')
            department_space_end.save()
            self.assertEqual(department_space_end.name, 'Department ')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_empty_space_end', result, 'Department(name="Department ")', 'Department ', department_space_end.name)


    def test_department_name_single_character(self, result='PASS', test_number=28):
        try:
            department_single = Department(name='D')
            department_single.save()
            self.assertEqual(department_single.name, 'D')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_single_character', result, 'Department(name="D")', 'D', department_single.name)


    def test_department_name_only_symbols(self, result='PASS', test_number=29):
        try:
            department_symbols = Department(name='@#$%^')
            department_symbols.save()
            self.assertEqual(department_symbols.name, '@#$%^')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_only_symbols', result, 'Department(name="@#$%^")', '@#$%^', department_symbols.name)


    def test_department_name_non_ascii(self, result='PASS', test_number=30):
        try:
            department_non_ascii = Department(name='部门')
            department_non_ascii.save()
            self.assertEqual(department_non_ascii.name, '部门')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_non_ascii', result, 'Department(name="部门")', '部门', department_non_ascii.name)

    
    @patch('dashboard.models.Department.save', lambda self: None)
    def test_department_name_emoji(self, result='PASS', test_number=31):
        try:
            department_emoji = Department(name='Department 🚀')
            department_emoji.save()
            self.assertEqual(department_emoji.name, 'Department 🚀')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_emoji', result, 'Department(name="Department 🚀")', 'Department 🚀', department_emoji.name)

    
    def test_department_name_performance_large_bulk_insert(self, result='PASS', test_number=32):
        try:
            departments = [Department(name=f'Department{i}') for i in range(1000)]
            Department.objects.bulk_create(departments)
            self.assertEqual(Department.objects.count(), 1000)
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_performance_large_bulk_insert', result, 'Bulk insert of 1000 departments', '1000', Department.objects.count())

    
    def test_department_name_partial_case_sensitivity(self, result='PASS', test_number=33):
        try:
            Department(name='Test Department').save()
            Department(name='test department').save()
            result = 'FAIL: No exception raised'
        except Exception as e:
            result = 'PASS'
        self.append_result(test_number, 'test_department_name_partial_case_sensitivity', result, 'Department(name="Test Department") and Department(name="test department")', 'Exception', str(e) if result != 'PASS' else 'Exception')

    
    def test_department_name_json_string(self, result='PASS', test_number=34):
        try:
            department_json = Department(name='{"department":"Finance"}')
            department_json.save()
            self.assertEqual(department_json.name, '{"department":"Finance"}')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_json_string', result, 'Department(name=\'{"department":"Finance"}\')', '{"department":"Finance"}', department_json.name)

    
    def test_department_name_numeric_edge_case(self, result='PASS', test_number=35):
        try:
            department_numeric = Department(name='000001')
            department_numeric.save()
            self.assertEqual(department_numeric.name, '000001')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_numeric_edge_case', result, 'Department(name="000001")', '000001', department_numeric.name)


    def test_department_name_single_quote(self, result='PASS', test_number=36):
        try:
            department_single_quote = Department(name="O'Reilly")
            department_single_quote.save()
            self.assertEqual(department_single_quote.name, "O'Reilly")
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_single_quote', result, 'Department(name="O\'Reilly")', "O'Reilly", department_single_quote.name)


    def test_department_name_sql_injection_like_input(self, result='PASS', test_number=37):
        try:
            department_sql_input = Department(name='DROP TABLE Departments;')
            department_sql_input.save()
            self.assertEqual(department_sql_input.name, 'DROP TABLE Departments;')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_sql_injection_like_input', result, 'Department(name="DROP TABLE Departments;")', 'DROP TABLE Departments;', department_sql_input.name)


    def test_department_name_html_content(self, result='PASS', test_number=38):
        try:
            department_html_content = Department(name='<h1>Department</h1>')
            department_html_content.save()
            self.assertEqual(department_html_content.name, '<h1>Department</h1>')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_html_content', result, 'Department(name="<h1>Department</h1>")', '<h1>Department</h1>', department_html_content.name)


    def test_department_name_with_tabs(self, result='PASS', test_number=39):
        try:
            department_tabs = Department(name="Dept\tDepartment")
            department_tabs.save()
            self.assertEqual(department_tabs.name, 'Dept\tDepartment')
        except Exception as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_with_tabs', result, 'Department(name="Dept\tDepartment")', 'Dept\tDepartment', department_tabs.name)


    def test_department_name_with_line_breaks(self, result='PASS', test_number=40):
        try:
            department_line_break = Department(name="Dept\nDepartment")
            department_line_break.save()
            self.assertEqual(department_line_break.name, 'Dept\nDepartment')
        except Exception as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_with_line_breaks', result, 'Department(name="Dept\nDepartment")', 'Dept\nDepartment', department_line_break.name)


    def test_department_name_with_emoji_in_the_middle(self, result='PASS', test_number=41):
        try:
            department_emoji_middle = Department(name="Dept 🏢 Department")
            department_emoji_middle.save()
            self.assertEqual(department_emoji_middle.name, 'Dept 🏢 Department')
        except Exception as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_with_emoji_in_the_middle', result, 'Department(name="Dept 🏢 Department")', 'Dept 🏢 Department', department_emoji_middle.name)


    def test_department_name_with_quotes(self, result='PASS', test_number=42):
        try:
            department_quotes = Department(name="Department with 'quotes'")
            department_quotes.save()
            self.assertEqual(department_quotes.name, "Department with 'quotes'")
        except Exception as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_with_quotes', result, 'Department(name="Department with \'quotes\'")', "Department with 'quotes'", department_quotes.name)


    def test_department_name_with_special_html_characters(self, result='PASS', test_number=43):
        try:
            department_html = Department(name='<script>alert(1)</script>')
            department_html.save()
        except Exception as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_with_special_html_characters', result, 'Department(name="<script>alert(1)</script>")', '<script>alert(1)</script>;', department_html.name)


    def test_department_name_with_unicode_combining_characters(self, result='PASS', test_number=44):
        try:
            department_unicode = Department(name='Cafe\u0301')
            department_unicode.save()
            self.assertEqual(department_unicode.name, 'Café')
        except Exception as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_with_unicode_combining_characters', result, 'Department(name="Cafe\u0301")', 'Café', department_unicode.name)


    def test_department_name_with_surrogate_pairs(self, result='PASS', test_number=45):
        try:
            department_surrogate = Department(name='𐍈')
            department_surrogate.save()
            self.assertEqual(department_surrogate.name, '𐍈')
        except Exception as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_with_surrogate_pairs', result, 'Department(name="𐍈")', '𐍈', department_surrogate.name)


    def test_department_name_with_emojis_at_start_and_end(self, result='PASS', test_number=46):
        try:
            department_emoji = Department(name='😀Department😀')
            department_emoji.save()
            self.assertEqual(department_emoji.name, '😀Department😀')
        except Exception as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_with_emojis_at_start_and_end', result, 'Department(name="😀Department😀")', '😀Department😀', department_emoji.name)


    def test_department_name_with_backslash(self, result='PASS', test_number=47):
        try:
            department_with_backslash = Department(name='Finance\\Department')
            department_with_backslash.save()
            self.assertEqual(department_with_backslash.name, 'Finance\\Department')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_with_backslash', result, 'Department(name="Finance\\Department")', 'Finance\\Department', department_with_backslash.name)


    def test_department_name_asterisk(self, result='PASS', test_number=48):
        try:
            department_asterisk = Department(name='*Sales*')
            department_asterisk.save()
            self.assertEqual(department_asterisk.name, '*Sales*')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_asterisk', result, 'Department(name="*Sales*")', '*Sales*', department_asterisk.name)


    def test_department_name_palindrome(self, result='PASS', test_number=49):
        try:
            department_palindrome = Department(name='radar')
            department_palindrome.save()
            self.assertEqual(department_palindrome.name, 'radar')
        except AssertionError as e:
            result = f'FAIL: {e}'
        self.append_result(test_number, 'test_department_name_palindrome', result, 'Department(name="radar")', 'radar', department_palindrome.name)


    # def test_department_name_utf8mb4(self, result='PASS', test_number=50):
    #     try:
    #         department_utf8mb4 = Department(name='Departamento🇲🇽')
    #         department_utf8mb4.save()
    #         self.assertEqual(department_utf8mb4.name, 'Departamento🇲🇽')
    #     except AssertionError as e:
    #         result = f'FAIL: {e}'
    #     self.append_result(test_number, 'test_department_name_utf8mb4', result, 'Department(name="Departamento🇲🇽")', 'Departamento🇲🇽', department_utf8mb4.name)
