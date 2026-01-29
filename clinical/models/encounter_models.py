from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from clinical.managers import EncounterManager
from shared.choices import BOOLEAN_CHOICES, ENCOUNTER_TYPE_CHOICES
from shared.validators import validate_numeric, validate_time

from .department_models import Department, EncounterSource
from .patient_provider_models import Patient, Provider


class MultiModalData(models.Model):
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
        return f"MMD{self.id}"

    class Meta:
        app_label = "clinical"
        verbose_name = "Multi Modal Data Path"
        verbose_name_plural = "Multi Modal Data Paths"


class Encounter(models.Model):
    csn_number = models.CharField(
        unique=True,
        max_length=10,
        verbose_name="CSN Number",
        null=True,
        blank=True,
        validators=[validate_numeric],
    )
    case_id = models.CharField(max_length=50, null=True, blank=True, verbose_name="Case ID")
    encounter_source = models.ForeignKey(
        EncounterSource, on_delete=models.CASCADE, verbose_name="Source", null=True, blank=True
    )
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    encounter_date_and_time = models.DateTimeField(
        default=timezone.now, verbose_name="Encounter Date and Time", validators=[validate_time]
    )
    provider_satisfaction = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(5)], default=0, verbose_name="Provider Satisfaction"
    )
    patient_satisfaction = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(5)], default=0, verbose_name="Patient Satisfaction"
    )
    multi_modal_data = models.OneToOneField(
        MultiModalData, on_delete=models.CASCADE, null=True, blank=True, related_name="encounter"
    )
    type = models.CharField(max_length=20, choices=ENCOUNTER_TYPE_CHOICES, default="clinic")
    is_deidentified = models.BooleanField(
        choices=BOOLEAN_CHOICES, default=False, verbose_name="Is Deidentified"
    )
    is_restricted = models.BooleanField(
        choices=BOOLEAN_CHOICES, default=True, verbose_name="Is Restricted"
    )
    tier_id = models.IntegerField(
        default=5,
        null=False,
        blank=False,
        db_index=True,  # Add index for frequent filtering
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="References accounts.Tier.id (1-5, defaults to 5 for highest restriction)",
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.type == "simcenter":
            return f"{self.case_id}"
        else:
            formatted_date = self.encounter_date_and_time.date().strftime("%m.%d.%Y")
            return f"{self.provider}_{self.patient}_{formatted_date}"

    def save(self, *args, **kwargs):
        from clinical.services import EncounterService

        # Delegate business logic to service class
        EncounterService.prepare_encounter_for_save(self)

        self.clean()
        super(Encounter, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if hasattr(self, "multi_modal_data") and self.multi_modal_data:
            self.multi_modal_data.delete()

        if self.type == "simcenter":
            if self.patient:
                self.patient.delete(using=kwargs.get("using"))
            if self.provider:
                self.provider.delete(using=kwargs.get("using"))
        super(Encounter, self).delete(*args, **kwargs)

    objects = EncounterManager()

    class Meta:
        app_label = "clinical"
        verbose_name = "Encounter"
        verbose_name_plural = "Encounters"
