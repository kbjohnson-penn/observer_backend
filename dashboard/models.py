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

GENDER_CATEGORIES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('UN', 'Unknown or Not Reported')
]


class Patient(models.Model):
    patient_id = models.CharField(max_length=200, unique=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=5, choices=GENDER_CATEGORIES)
    race = models.CharField(max_length=5, choices=RACIAL_CATEGORIES)
    ethnicity = models.CharField(max_length=5, choices=ETHNIC_CATEGORIES)

    def __str__(self):
        return f'{self.patient_id}'


class Provider(models.Model):
    provider_id = models.CharField(max_length=200, unique=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=5, choices=GENDER_CATEGORIES)
    race = models.CharField(max_length=5, choices=RACIAL_CATEGORIES)
    ethnicity = models.CharField(max_length=5, choices=ETHNIC_CATEGORIES)

    def __str__(self):
        return f'{self.provider_id}'


class Department(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class MultiModalDataPath(models.Model):
    multi_modal_data_id = models.CharField(max_length=200, unique=True)
    provider_view = models.FileField(upload_to='media/encouter/provider_views/', null=True, blank=True)
    patient_view = models.FileField(upload_to='media/encouter/patient_views/', null=True, blank=True)
    room_view = models.FileField(upload_to='media/encouter/room_views/', null=True, blank=True)
    audio = models.FileField(upload_to='media/encouter/audios/', null=True, blank=True)
    transcript = models.FileField(upload_to='media/encouter/transcripts/', null=True, blank=True)
    patient_survey_path = models.FileField(upload_to='media/encouter/patient_surveys/', null=True, blank=True)
    provider_survey_path = models.FileField(upload_to='media/encouter/provider_surveys/', null=True, blank=True)

    def __str__(self):
        return f'{self.multi_modal_data_id}'

class Encounter(models.Model):
    case_id = models.CharField(max_length=200, unique=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    multi_modal_data = models.ForeignKey(MultiModalDataPath, on_delete=models.CASCADE, null=True, blank=True)
    encounter_date = models.DateField(default=datetime.now)
    encounter_time = models.DateTimeField(default=datetime.now)
    is_deidentified = models.BooleanField(choices=BOOLEAN_CHOICES, default=True)
    is_restricted = models.BooleanField(choices=BOOLEAN_CHOICES, default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.case_id}'


class AnonymizedMapping(models.Model):
    encounter = models.OneToOneField(
        Encounter, on_delete=models.CASCADE, unique=True)
    anonymized_encounter_id = models.CharField(max_length=255, unique=True)
    anonymized_patient_id = models.CharField(max_length=255)
    anonymized_provider_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.anonymized_encounter_id}'