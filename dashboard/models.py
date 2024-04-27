from django import forms
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from datetime import datetime
from django.utils import timezone
import re

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
    patient_id = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    sex = models.CharField(max_length=5, choices=SEX_CATEGORIES, blank=True)
    race = models.CharField(
        max_length=5, choices=RACIAL_CATEGORIES, blank=True)
    ethnicity = models.CharField(
        max_length=5, choices=ETHNIC_CATEGORIES, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.patient_id}'

    def clean_patient_id(self, patient_id):
        # Check if patient_id only contains numbers
        if not re.match('^[0-9]+$', patient_id):
            raise forms.ValidationError(
                "patient_id should only contain numbers")

        # Remove leading zeros from patient_id
        patient_id = str(int(patient_id.lstrip('0')))
        # Attach 'P' to the patient_id
        patient_id = 'P' + patient_id

        # Check if patient_id already exists in the database
        if Patient.objects.filter(patient_id=patient_id).exists():
            raise forms.ValidationError("patient_id already exists")

        return patient_id

    def save(self, *args, **kwargs):
        self.patient_id = self.clean_patient_id(self.patient_id)
        super(Patient, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'


class Provider(models.Model):
    provider_id = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    sex = models.CharField(max_length=5, choices=SEX_CATEGORIES, blank=True)
    race = models.CharField(
        max_length=5, choices=RACIAL_CATEGORIES, blank=True)
    ethnicity = models.CharField(
        max_length=5, choices=ETHNIC_CATEGORIES, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.provider_id}'

    def clean_provider_id(self, provider_id):
        # Check if provider_id only contains numbers
        if not re.match('^[0-9]+$', provider_id):
            raise ValidationError("provider_id should only contain numbers")

        # Remove leading zeros from provider_id
        provider_id = str(int(provider_id.lstrip('0')))
        # Attach 'PR' to the provider_id
        provider_id = 'PR' + provider_id

        # Check if provider_id already exists in the database
        if Provider.objects.filter(provider_id=provider_id).exists():
            raise forms.ValidationError("provider_id already exists")

        return provider_id

    def save(self, *args, **kwargs):
        self.provider_id = self.clean_provider_id(self.provider_id)
        super(Provider, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Provider'
        verbose_name_plural = 'Providers'


class EncounterSource(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Encounter Source'
        verbose_name_plural = 'Encounter Source'


class Department(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'


class MultiModalDataPath(models.Model):
    multi_modal_data_id = models.CharField(
        max_length=255, unique=True, verbose_name="Multi Modal Data ID")
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

    def clean_multi_modal_data_id(self, multi_modal_data_id):
        # Check if multi_modal_data_id only contains numbers
        if not re.match('^[0-9]+$', multi_modal_data_id):
            raise ValidationError(
                "multi_modal_data_id should only contain numbers")

        # Remove leading zeros from multi_modal_data_id
        multi_modal_data_id = str(int(multi_modal_data_id.lstrip('0')))
        # Attach 'MMD' to the multi_modal_data_id
        multi_modal_data_id = 'MMD' + multi_modal_data_id
        return multi_modal_data_id

    def save(self, *args, **kwargs):
        self.multi_modal_data_id = self.clean_multi_modal_data_id(
            self.multi_modal_data_id)
        super(MultiModalDataPath, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Multi Modal Data Path'
        verbose_name_plural = 'Multi Modal Data Paths'


class Encounter(models.Model):
    case_id = models.CharField(max_length=255, unique=True)
    encounter_source = models.ForeignKey(
        EncounterSource, on_delete=models.CASCADE, verbose_name="Encounter Source")
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE)
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, blank=True)
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, blank=True)
    multi_modal_data = models.ForeignKey(
        MultiModalDataPath, on_delete=models.CASCADE, verbose_name="Multi Modal Data Path")
    encounter_date_and_time = models.DateTimeField(
        default=datetime.now, verbose_name="Encounter Date and Time")
    provider_satisfaction = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0,
        verbose_name="Provider Satisfaction"
    )
    patient_satisfaction = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0,
        verbose_name="Patient Satisfaction"
    )
    is_deidentified = models.BooleanField(
        choices=BOOLEAN_CHOICES, default=False, verbose_name="Is Deidentified")
    is_restricted = models.BooleanField(
        choices=BOOLEAN_CHOICES, default=True, verbose_name="Is Restricted")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.case_id}'

    def clean_case_id(self, case_id):
        # Check if case_id only contains numbers
        if not re.match('^[0-9]+$', case_id):
            raise ValidationError("case_id should only contain numbers")

        # Remove leading zeros from case_id
        case_id = str(int(case_id.lstrip('0')))
        # Attach 'E' to the case_id
        case_id = 'E' + case_id
        return case_id

    def clean(self):
        if self.patient_satisfaction < 0:
            raise ValidationError('Patient satisfaction cannot be negative.')

        if self.provider_satisfaction < 0:
            raise ValidationError('Provider satisfaction cannot be negative.')

    def save(self, *args, **kwargs):
        self.case_id = self.clean_case_id(self.case_id)

        if timezone.is_naive(self.encounter_date_and_time):
            self.encounter_date_and_time = timezone.make_aware(
                self.encounter_date_and_time)

        self.clean()

        super(Encounter, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Encounter'
        verbose_name_plural = 'Encounters'
