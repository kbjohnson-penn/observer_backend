from django.db import models

from clinical.managers import PatientManager, ProviderManager
from shared.choices import ETHNIC_CATEGORIES, RACIAL_CATEGORIES, SEX_CATEGORIES
from shared.validators import validate_field, validate_time


class Patient(models.Model):
    patient_id = models.PositiveIntegerField(unique=True)
    first_name = models.CharField(max_length=255, blank=True, validators=[validate_field])
    last_name = models.CharField(max_length=255, blank=True, validators=[validate_field])
    date_of_birth = models.DateField(blank=True, null=True, validators=[validate_time])
    sex = models.CharField(max_length=5, choices=SEX_CATEGORIES, blank=True)
    race = models.CharField(max_length=5, choices=RACIAL_CATEGORIES, blank=True)
    ethnicity = models.CharField(max_length=5, choices=ETHNIC_CATEGORIES, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PT{self.patient_id}"

    objects = PatientManager()

    class Meta:
        app_label = "clinical"
        verbose_name = "Patient"
        verbose_name_plural = "Patients"


class Provider(models.Model):
    provider_id = models.PositiveIntegerField(unique=True)
    first_name = models.CharField(max_length=255, blank=True, validators=[validate_field])
    last_name = models.CharField(max_length=255, blank=True, validators=[validate_field])
    date_of_birth = models.DateField(blank=True, null=True, validators=[validate_time])
    sex = models.CharField(max_length=5, choices=SEX_CATEGORIES, blank=True)
    race = models.CharField(max_length=5, choices=RACIAL_CATEGORIES, blank=True)
    ethnicity = models.CharField(max_length=5, choices=ETHNIC_CATEGORIES, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PR{self.provider_id}"

    objects = ProviderManager()

    class Meta:
        app_label = "clinical"
        verbose_name = "Provider"
        verbose_name_plural = "Providers"
