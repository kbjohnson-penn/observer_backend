from django.db import models
from django.core.validators import MaxValueValidator
from django.core.exceptions import ValidationError
from datetime import datetime
from django.utils import timezone

from .patient_models import Patient
from .provider_models import Provider
from .source_and_department_models import EncounterSource, Department

BOOLEAN_CHOICES = [
    (True, 'Yes'),
    (False, 'No'),
]


ENCOUNTER_TYPE_CHOICES = [
    ('clinic', 'Clinic'),
    ('simcenter', 'Sim Center'),
    ('rias', 'RIAS'),
]


FILE_TYPE_CHOICES = [
    ('room_view', 'Room View'),
    ('provider_view', 'Provider View'),
    ('patient_view', 'Patient View'),
    ('audio', 'Audio'),
    ('transcript', 'Transcript'),
    ('patient_survey', 'Patient Survey'),
    ('provider_survey', 'Provider Survey'),
    ('patient_annotation', 'Patient Annotation'),
    ('provider_annotation', 'Provider Annotation'),
    ('rias_transcript', 'RIAS Transcript'),
    ('rias_codes', 'RIAS Codes'),
    ('other', 'Other'),
]
FILE_TYPE_CHOICES_DICT = dict(FILE_TYPE_CHOICES)


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
        unique=True,
        max_length=10,
        verbose_name="CSN Number",
        null=True,
        blank=True
    )
    case_id = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Case ID")
    encounter_source = models.ForeignKey(
        EncounterSource,
        on_delete=models.CASCADE,
        verbose_name="Source",
        null=True,
        blank=True
    )
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE)
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE)
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE)
    encounter_date_and_time = models.DateTimeField(
        default=datetime.now, verbose_name="Encounter Date and Time")
    provider_satisfaction = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(5)],
        default=0,
        verbose_name="Provider Satisfaction"
    )
    patient_satisfaction = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(5)],
        default=0,
        verbose_name="Patient Satisfaction"
    )
    multi_modal_data = models.OneToOneField(
        MultiModalData, on_delete=models.CASCADE, null=True, blank=True, related_name='encounter')
    type = models.CharField(
        max_length=20, choices=ENCOUNTER_TYPE_CHOICES, default='clinic')
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
            raise ValidationError("Patient satisfaction cannot be negative.")

        if self.provider_satisfaction < 0:
            raise ValidationError("Provider satisfaction cannot be negative.")

    def save(self, *args, **kwargs):
        if self.type == 'clinic':
            self.encounter_source, created = EncounterSource.objects.get_or_create(
                name='Clinic')
        elif self.type == 'simcenter':
            self.encounter_source, created = EncounterSource.objects.get_or_create(
                name='SimCenter')
        elif self.type == 'rias':
            self.encounter_source, created = EncounterSource.objects.get_or_create(
                name='RIAS')

        if timezone.is_naive(self.encounter_date_and_time):
            self.encounter_date_and_time = timezone.make_aware(
                self.encounter_date_and_time)

        self.clean()

        super(Encounter, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        MultiModalData.objects.filter(encounter=self).delete()
        super(Encounter, self).delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Encounter'
        verbose_name_plural = 'Encounters'


class EncounterFile(models.Model):
    encounter = models.ForeignKey(
        Encounter, related_name='files', on_delete=models.CASCADE, null=True, blank=True)
    encounter_source = models.ForeignKey(
        EncounterSource, on_delete=models.CASCADE, null=True, blank=True)
    file_type = models.CharField(
        max_length=50, choices=FILE_TYPE_CHOICES, blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{FILE_TYPE_CHOICES_DICT.get(self.file_type, "Unknown")}'
