from django.db import models, transaction
from django.core.validators import MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime
import random

from .patient_models import Patient
from .provider_models import Provider
from .source_and_department_models import EncounterSource, Department
from .profile_models import Tier
from ..choices import BOOLEAN_CHOICES, ENCOUNTER_TYPE_CHOICES, FILE_TYPE_CHOICES, FILE_TYPE_CHOICES_DICT


class MultiModalData(models.Model):
    provider_view = models.BooleanField(
        default=False, verbose_name="Provider View")
    patient_view = models.BooleanField(
        default=False, verbose_name="Patient View")
    room_view = models.BooleanField(default=False, verbose_name="Room View")
    audio = models.BooleanField(default=False, verbose_name="Audio")
    transcript = models.BooleanField(default=False, verbose_name="Transcript")
    patient_survey = models.BooleanField(
        default=False, verbose_name="Patient Survey")
    provider_survey = models.BooleanField(
        default=False, verbose_name="Provider Survey")
    patient_annotation = models.BooleanField(
        default=False, verbose_name="Patient Annotation")
    provider_annotation = models.BooleanField(
        default=False, verbose_name="Provider Annotation")
    rias_transcript = models.BooleanField(
        default=False, verbose_name="RIAS Transcript")
    rias_codes = models.BooleanField(default=False, verbose_name="RIAS Codes")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'MMD{self.id}'

    class Meta:
        verbose_name = 'Multi Modal Data Path'
        verbose_name_plural = 'Multi Modal Data Paths'


class Encounter(models.Model):
    csn_number = models.CharField(
        unique=True, max_length=10, verbose_name="CSN Number", null=True, blank=True)
    case_id = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Case ID")
    encounter_source = models.ForeignKey(
        EncounterSource, on_delete=models.CASCADE, verbose_name="Source", null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, null=True, blank=True)
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, null=True, blank=True)
    encounter_date_and_time = models.DateTimeField(
        default=datetime.now, verbose_name="Encounter Date and Time")
    provider_satisfaction = models.PositiveSmallIntegerField(validators=[MaxValueValidator(
        5)], default=0, verbose_name="Provider Satisfaction", null=True, blank=True)
    patient_satisfaction = models.PositiveSmallIntegerField(validators=[MaxValueValidator(
        5)], default=0, verbose_name="Patient Satisfaction", null=True, blank=True)
    multi_modal_data = models.OneToOneField(
        MultiModalData, on_delete=models.CASCADE, null=True, blank=True, related_name='encounter')
    type = models.CharField(
        max_length=20, choices=ENCOUNTER_TYPE_CHOICES, default='clinic')
    is_deidentified = models.BooleanField(
        choices=BOOLEAN_CHOICES, default=False, verbose_name="Is Deidentified")
    is_restricted = models.BooleanField(
        choices=BOOLEAN_CHOICES, default=True, verbose_name="Is Restricted")
    tier = models.ForeignKey(Tier, related_name='encounters',
                             on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.type == 'clinic':
            formatted_date = self.encounter_date_and_time.date().strftime('%m.%d.%Y')
            return f'{self.provider}_{self.patient}_{formatted_date}'
        else:
            return f'{self.case_id}'

    def clean(self):
        if self.patient_satisfaction < 0:
            raise ValidationError("Patient satisfaction cannot be negative.")
        if self.provider_satisfaction < 0:
            raise ValidationError("Provider satisfaction cannot be negative.")

    def save(self, *args, **kwargs):
        if not self.pk:
            if not self.encounter_source:
                self.encounter_source, _ = EncounterSource.objects.get_or_create(
                    name=self.type.capitalize()
                )

            if timezone.is_naive(self.encounter_date_and_time):
                self.encounter_date_and_time = timezone.make_aware(
                    self.encounter_date_and_time
                )

            with transaction.atomic():
                if not self.patient:
                    self.patient = Patient.objects.create(
                        patient_id=random.randint(100000, 999999)
                    )
                if not self.provider:
                    self.provider = Provider.objects.create(
                        provider_id=random.randint(100000, 999999)
                    )

        if self.type != 'clinic':
            self.provider_satisfaction = 0
            self.patient_satisfaction = 0
            self.is_deidentified = False
            self.is_restricted = True

        self.clean()
        super(Encounter, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        MultiModalData.objects.filter(encounter=self).delete()
        if self.patient:
            self.patient.delete()
        if self.provider:
            self.provider.delete()
        super(Encounter, self).delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Encounter'
        verbose_name_plural = 'Encounters'


class EncounterFile(models.Model):
    encounter = models.ForeignKey(
        Encounter, related_name='files', on_delete=models.CASCADE, null=True, blank=True)
    file_type = models.CharField(
        max_length=50, choices=FILE_TYPE_CHOICES, blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{FILE_TYPE_CHOICES_DICT.get(self.file_type, "Unknown")}'
