from django.db import models

DEPARTMENTS_NAMES = [
    'sim-center',
    'oncology',
    'primary-care',
    'neurology',
    'fmaily-medicine',
]

ENCOUNTER_MEDIA_TYPE_CHOICES = [
    ('VATO', 'Video + Audio + Transcript + Annotations'),
    ('VAT', 'Video + Audio + Transcript'),
    ('VA', 'Video + Audio'),
    ('AT', 'Audio + Transcript'),
    ('VT', 'Video + Transcript'),
    ('VO', 'Video + Annotations'),
    ('AO', 'Audio + Annotations'),
    ('TO', 'Transcript + Annotations'),
    ('VAT', 'Video + Audio + Transcript'),
    ('VAO', 'Video + Audio + Annotations'),
    ('VTO', 'Video + Transcript + Annotations'),
    ('ATO', 'Audio + Transcript + Annotations'),
    ('V', 'Video Only'),
    ('A', 'Audio Only'),
    ('T', 'Transcript Only'),
    ('O', 'Annotations Only'),
    ('OTH', 'Others'),
]

BOOLEAN_CHOICES = [
    (True, 'Yes'),
    (False, 'No'),
]


class Department(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Encounter(models.Model):
    case_id = models.CharField(max_length=200, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    visit_type = models.CharField(
        max_length=10, choices=ENCOUNTER_MEDIA_TYPE_CHOICES, default='VAT')
    is_deidentified = models.BooleanField(
        choices=BOOLEAN_CHOICES, default=False)
    is_restricted = models.BooleanField(choices=BOOLEAN_CHOICES, default=True)
    visit_date = models.DateField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.case_id
