from django.test import TestCase
from dashboard.models import Department


class DepartmentModelTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name='Test Department')

    def test_department_creation(self):
        self.assertEqual(Department.objects.count(), 1)
        self.assertEqual(self.department.name, 'Test Department')

    def test_department_str(self):
        self.assertEqual(str(self.department), 'Test Department')