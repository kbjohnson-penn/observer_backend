from django.db import models

DEPARTMENTS_NAMES = [
    'sim-center',
    'oncology',
    'primary-care',
    'neurology',
    'fmaily-medicine',
]

ENCOUNTER_MEDIA_TYPE_CHOICES = [
    ('Video', 'Video'),
    ('Audio', 'Audio'),
    ('Transcript', 'Transcript'),
    ('Annotation', 'Annotation'),
]

BOOLEAN_CHOICES = [
    (True, 'Yes'),
    (False, 'No'),
]

RACIAL_CATEGORIES = [
    ('AI', 'American Indian or Alaska Native'),
    ('A', 'Asian'),
    ('NHPI', 'Native Hawaiian or Other Pacific Islander'),
    ('B', 'Black or African American'),
    ('W', 'White'),
    ('M', 'More than One Race'),
    ('UN', 'Unknown or Not Reported'),
]

ETHNIC_CATEGORIES = [
    ('H', 'Hispanic or Latino'),
    ('NH', 'Not Hispanic or Latino'),
    ('UN', 'Unknown or Not Reported Ethnicity'),
]

GENDER_CATEGORIES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('UN', 'Unknown or Not Reported')
]

AGE_RANGES = [
    ('18-20', '18-20'),
    ('21-30', '21-30'),
    ('31-40', '31-40'),
    ('41-50', '41-50'),
    ('51-60', '51-60'),
    ('61-70', '61-70'),
    ('71-80', '71-80'),
    ('81+', '81+'),
    ('UN', 'Unknown or Not Reported'),
]


class Choice(models.Model):
    name = models.CharField(max_length=10, choices=ENCOUNTER_MEDIA_TYPE_CHOICES)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Encounter(models.Model):
    case_id = models.CharField(max_length=200, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    racial_category = models.CharField(
        max_length=4, choices=RACIAL_CATEGORIES, null=True)
    ethnic_category = models.CharField(
        max_length=2, choices=ETHNIC_CATEGORIES, null=True)
    gender = models.CharField(
        max_length=2, choices=GENDER_CATEGORIES, null=True)
    age_range = models.CharField(max_length=5, choices=AGE_RANGES, null=True)
    visit_date = models.DateField()
    media_types = models.ManyToManyField(Choice)
    is_deidentified = models.BooleanField(
        choices=BOOLEAN_CHOICES, default=False)
    is_restricted = models.BooleanField(choices=BOOLEAN_CHOICES, default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.case_id
