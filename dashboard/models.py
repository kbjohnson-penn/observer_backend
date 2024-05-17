from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from datetime import datetime
from django.utils import timezone

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
    patient_id = models.IntegerField(unique=True)
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
        return f'PT{self.patient_id}'

    class Meta:
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'


class Provider(models.Model):
    provider_id = models.IntegerField(unique=True)
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
        return f'PR{self.provider_id}'

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
        return f'MMD{self.id}'

    class Meta:
        verbose_name = 'Multi Modal Data Path'
        verbose_name_plural = 'Multi Modal Data Paths'


class Encounter(models.Model):
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
        formatted_date = self.encounter_date_and_time.date().strftime('%m.%d.%Y')
        return f'{self.provider}_{self.patient}_{formatted_date}'

    def clean(self):
        if self.patient_satisfaction < 0:
            raise ValidationError('Patient satisfaction cannot be negative.')

        if self.provider_satisfaction < 0:
            raise ValidationError('Provider satisfaction cannot be negative.')

    def save(self, *args, **kwargs):
        if timezone.is_naive(self.encounter_date_and_time):
            self.encounter_date_and_time = timezone.make_aware(
                self.encounter_date_and_time)

        self.clean()

        super(Encounter, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Encounter'
        verbose_name_plural = 'Encounters'
