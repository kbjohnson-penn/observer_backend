from django.db import models
from datetime import datetime

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

SEX_CATEGORIES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('UN', 'Unknown or Not Reported')
]


class Patient(models.Model):
    patient_id = models.CharField(max_length=200, unique=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=5, choices=SEX_CATEGORIES)
    race = models.CharField(max_length=5, choices=RACIAL_CATEGORIES)
    ethnicity = models.CharField(max_length=5, choices=ETHNIC_CATEGORIES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.patient_id}'

    class Meta:
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'


class Provider(models.Model):
    provider_id = models.CharField(max_length=200, unique=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=5, choices=SEX_CATEGORIES)
    race = models.CharField(max_length=5, choices=RACIAL_CATEGORIES)
    ethnicity = models.CharField(max_length=5, choices=ETHNIC_CATEGORIES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.provider_id}'

    class Meta:
        verbose_name = 'Provider'
        verbose_name_plural = 'Providers'


class Department(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'


class MultiModalDataPath(models.Model):
    multi_modal_data_id = models.CharField(
        max_length=200, unique=True, verbose_name="Multi Modal Data ID")
    provider_view = models.URLField(
        max_length=200, null=True, blank=True, verbose_name="Provider View")
    patient_view = models.URLField(
        max_length=200, null=True, blank=True, verbose_name="Patient View")
    room_view = models.URLField(
        max_length=200, null=True, blank=True, verbose_name="Room View")
    audio = models.URLField(max_length=200, null=True,
                            blank=True, verbose_name="Audio")
    transcript = models.URLField(
        max_length=200, null=True, blank=True, verbose_name="Transcript")
    patient_survey = models.URLField(
        max_length=200, null=True, blank=True, verbose_name="Patient Survey")
    provider_survey = models.URLField(
        max_length=200, null=True, blank=True, verbose_name="Provider Survey")
    rias_transcript = models.URLField(
        max_length=200, null=True, blank=True, verbose_name="RIAS Transcript")
    rias_codes = models.URLField(
        max_length=200, null=True, blank=True, verbose_name="RIAS Codes")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.multi_modal_data_id}'

    class Meta:
        verbose_name = 'Multi Modal Data Path'
        verbose_name_plural = 'Multi Modal Data Paths'


class Encounter(models.Model):
    case_id = models.CharField(max_length=200, unique=True)
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE)
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE)
    multi_modal_data = models.ForeignKey(
        MultiModalDataPath, on_delete=models.CASCADE, null=True, blank=True)
    encounter_date_and_time = models.DateTimeField(default=datetime.now)
    patient_satisfaction = models.IntegerField(default=0)
    provider_satisfaction = models.IntegerField(default=0)
    is_deidentified = models.BooleanField(
        choices=BOOLEAN_CHOICES, default=False)
    is_restricted = models.BooleanField(choices=BOOLEAN_CHOICES, default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.case_id}'

    class Meta:
        verbose_name = 'Encounter'
        verbose_name_plural = 'Encounters'


class RIAS(models.Model):
    rias_case_id = models.CharField(
        max_length=200, unique=True, verbose_name="RIAS Case ID")
    multi_modal_data = models.ForeignKey(
        MultiModalDataPath, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Multi Modal Data")
    is_deidentified = models.BooleanField(
        choices=BOOLEAN_CHOICES, default=False, verbose_name="Is Deidentified")
    is_restricted = models.BooleanField(
        choices=BOOLEAN_CHOICES, default=True, verbose_name="Is Restricted")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.rias_case_id}'

    class Meta:
        verbose_name = 'RIAS'
        verbose_name_plural = 'RIAS Codes'
