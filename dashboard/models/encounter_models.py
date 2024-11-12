from django.db import models, transaction
from django.core.validators import MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from datetime import datetime
from django.utils import timezone
import random

from .patient_models import Patient
from .provider_models import Provider

BOOLEAN_CHOICES = [
    (True, 'Yes'),
    (False, 'No'),
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

class EncounterSource(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Source'
        verbose_name_plural = 'Source'


class Department(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'


class MultiModalDataPath(models.Model):
    provider_view = models.BooleanField(default=False, verbose_name="Provider View")
    patient_view = models.BooleanField(default=False, verbose_name="Patient View")
    room_view = models.BooleanField(default=False, verbose_name="Room View")
    audio = models.BooleanField(default=False, verbose_name="Audio")
    transcript = models.BooleanField(default=False, verbose_name="Transcript")
    patient_survey = models.BooleanField(default=False, verbose_name="Patient Survey")
    provider_survey = models.BooleanField(default=False, verbose_name="Provider Survey")
    patient_annotation = models.BooleanField(default=False, verbose_name="Patient Annotation")
    provider_annotation = models.BooleanField(default=False, verbose_name="Provider Annotation")
    rias_transcript = models.BooleanField(default=False, verbose_name="RIAS Transcript")
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
    )
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
    is_deidentified = models.BooleanField(
        choices=BOOLEAN_CHOICES, default=False, verbose_name="Is Deidentified")
    is_restricted = models.BooleanField(
        choices=BOOLEAN_CHOICES, default=True, verbose_name="Is Restricted")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    multi_modal_data = models.OneToOneField(MultiModalDataPath, on_delete=models.CASCADE, null=True, blank=True, related_name='encounter')

    def __str__(self):
        formatted_date = self.encounter_date_and_time.date().strftime('%m.%d.%Y')
        return f'{self.provider}_{self.patient}_{formatted_date}'

    def clean(self):
        if self.patient_satisfaction < 0:
            raise ValidationError("Patient satisfaction cannot be negative.")

        if self.provider_satisfaction < 0:
            raise ValidationError("Provider satisfaction cannot be negative.")

    def save(self, *args, **kwargs):
        self.encounter_source, created = EncounterSource.objects.get_or_create(
            name='Clinic')

        if timezone.is_naive(self.encounter_date_and_time):
            self.encounter_date_and_time = timezone.make_aware(self.encounter_date_and_time)

        self.clean()

        super(Encounter, self).save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        MultiModalDataPath.objects.filter(encounter=self).delete()
        
        super(Encounter, self).delete(*args, **kwargs)
        

    class Meta:
        verbose_name = 'Encounter (Clinic)'
        verbose_name_plural = 'Encounters (Clinic)'


class EncounterSimCenter(models.Model):
    encounter_source = models.ForeignKey(
        EncounterSource,
        on_delete=models.CASCADE,
        verbose_name="Source",
        null=True,
        blank=True
    )
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, blank=True, null=True)
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, blank=True, null=True)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE)
    case_id = models.CharField(max_length=255, verbose_name="Case ID")
    encounter_date_and_time = models.DateTimeField(
        default=datetime.now, verbose_name="Encounter Date and Time")
    is_deidentified = models.BooleanField(
        choices=BOOLEAN_CHOICES, default=False, verbose_name="Is Deidentified")
    is_restricted = models.BooleanField(
        choices=BOOLEAN_CHOICES, default=True, verbose_name="Is Restricted")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    multi_modal_data = models.OneToOneField(MultiModalDataPath, on_delete=models.CASCADE, null=True, blank=True, related_name='encounter_sim_center')

    def save(self, *args, **kwargs):
        self.encounter_source, created = EncounterSource.objects.get_or_create(
            name='SimCenter')

        with transaction.atomic():
            if not self.patient:
                patient = Patient.objects.create(
                    patient_id=random.randint(100000, 999999))
                self.patient = patient

            if not self.provider:
                provider = Provider.objects.create(
                    provider_id=random.randint(100000, 999999))
                self.provider = provider

        super(EncounterSimCenter, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        EncounterFile.objects.filter(encounter_sim_center=self).delete()
        MultiModalDataPath.objects.filter(encounter_sim_center=self).delete()
        if self.patient:
            self.patient.delete()
        if self.provider:
            self.provider.delete()
        super(EncounterSimCenter, self).delete(*args, **kwargs)

    def __str__(self):
        return f'{self.case_id}'

    class Meta:
        verbose_name = 'Encounter (Sim Center)'
        verbose_name_plural = 'Encounters (Sim Center)'


class EncounterRIAS(models.Model):
    encounter_source = models.ForeignKey(
        EncounterSource,
        on_delete=models.CASCADE,
        verbose_name="Source",
        null=True,
        blank=True
    )
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, blank=True, null=True)
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, blank=True, null=True)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE)
    case_id = models.CharField(max_length=255, verbose_name="Case ID")
    is_deidentified = models.BooleanField(
        choices=BOOLEAN_CHOICES, default=False, verbose_name="Is Deidentified")
    is_restricted = models.BooleanField(
        choices=BOOLEAN_CHOICES, default=True, verbose_name="Is Restricted")
    timestamp = models.DateTimeField(auto_now_add=True)

    multi_modal_data = models.OneToOneField(MultiModalDataPath, on_delete=models.CASCADE, null=True, blank=True, related_name='encounter_rias')

    def save(self, *args, **kwargs):
        self.encounter_source, created = EncounterSource.objects.get_or_create(
            name='RIAS')

        with transaction.atomic():
            if not self.patient:
                patient = Patient.objects.create(
                    patient_id=random.randint(100000, 999999))
                self.patient = patient

            if not self.provider:
                provider = Provider.objects.create(
                    provider_id=random.randint(100000, 999999))
                self.provider = provider

        super(EncounterRIAS, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        EncounterFile.objects.filter(encounter_rias=self).delete()
        MultiModalDataPath.objects.filter(encounter_rias=self).delete()
        if self.patient:
            self.patient.delete()
        if self.provider:
            self.provider.delete()
        super(EncounterRIAS, self).delete(*args, **kwargs)

    def __str__(self):
        return f'{self.case_id}'

    class Meta:
        verbose_name = 'Encounter (RIAS)'
        verbose_name_plural = 'Encounters (RIAS)'


class EncounterFile(models.Model):
    encounter = models.ForeignKey(Encounter, related_name='files', on_delete=models.CASCADE, null=True, blank=True)
    encounter_sim_center = models.ForeignKey(EncounterSimCenter, related_name='files', on_delete=models.CASCADE, null=True, blank=True)
    encounter_rias = models.ForeignKey(EncounterRIAS, related_name='files', on_delete=models.CASCADE, null=True, blank=True)
    encounter_source = models.ForeignKey(EncounterSource, on_delete=models.CASCADE, null=True, blank=True)
    file_type = models.CharField(max_length=50, choices=FILE_TYPE_CHOICES, blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{FILE_TYPE_CHOICES_DICT.get(self.file_type, "Unknown")}'