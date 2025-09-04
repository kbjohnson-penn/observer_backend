from django.db import models
from .person_provider_models import Person, Provider


class VisitOccurrence(models.Model):
    """
    This table records details about each healthcare encounter or visit a person has.
    """
    person_id = models.ForeignKey('Person', on_delete=models.CASCADE, db_column='person_id')
    provider_id = models.ForeignKey('Provider', on_delete=models.CASCADE, db_column='provider_id')
    visit_start_date = models.DateField(null=True, blank=True)
    visit_start_time = models.TimeField(null=True, blank=True)
    visit_source_value = models.CharField(max_length=255)
    visit_source_id = models.IntegerField()
    tier_id = models.IntegerField(help_text="Tier level for data access control")

    def __str__(self):
        return f"Visit Occurrence ID ({self.id})"

    class Meta:
        app_label = 'research'
        db_table = 'visit_occurrence'

class Note(models.Model):
    """
    This table stores clinical notes and their associated metadata.
    """
    person_id = models.ForeignKey(Person, on_delete=models.CASCADE, db_column='person_id')
    provider_id = models.ForeignKey(Provider, on_delete=models.CASCADE, db_column='provider_id')
    visit_occurrence_id = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, db_column='visit_occurrence_id')
    note_date = models.DateField()
    note_text = models.TextField()
    note_type = models.CharField(max_length=255)
    note_status = models.CharField(max_length=255)

    def __str__(self):
        return f"Note ID ({self.id})"
    class Meta:
        app_label = 'research'
        db_table = 'note'


class ConditionOccurrence(models.Model):
    """
    This table captures information about conditions or diagnoses recorded for a patient.
    """
    visit_occurrence_id = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, db_column='visit_occurrence_id')
    is_primary_dx = models.CharField(max_length=255)
    condition_source_value = models.CharField(max_length=255)
    condition_concept_id = models.IntegerField()
    concept_code = models.CharField(max_length=255)

    def __str__(self):
        return f"Condition Occurrence ID ({self.id})"
    class Meta:
        app_label = 'research'
        db_table = 'condition_occurrence'


class DrugExposure(models.Model):
    """
    This table records details about a patient's exposure to specific drugs.
    """
    visit_occurrence_id = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, db_column='visit_occurrence_id')
    drug_ordering_date = models.DateField(null=True, blank=True)
    drug_exposure_start_datetime = models.DateTimeField(null=True, blank=True)
    drug_exposure_end_datetime = models.DateTimeField(null=True, blank=True)
    description = models.CharField(max_length=255)
    quantity = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Drug Exposure ID ({self.id})"
    class Meta:
        app_label = 'research'
        db_table = 'drug_exposure'


class ProcedureOccurrence(models.Model):
    """
    This table documents procedures performed on patients.
    """
    visit_occurrence_id = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, db_column='visit_occurrence_id')
    procedure_ordering_date = models.DateField()
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    future_or_stand = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Procedure Occurrence ID ({self.id})"
    class Meta:
        app_label = 'research'
        db_table = 'procedure_occurrence'


class Measurement(models.Model):
    """
    This table stores quantitative measurements and observations taken during a visit.
    """
    visit_occurrence_id = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, db_column='visit_occurrence_id')
    bp_systolic = models.IntegerField(null=True, blank=True)
    bp_diastolic = models.IntegerField(null=True, blank=True)
    phys_bp = models.CharField(max_length=255, null=True, blank=True)
    weight_lb = models.FloatField(null=True, blank=True)
    height = models.CharField(max_length=255, null=True, blank=True)
    pulse = models.IntegerField(null=True, blank=True)
    phys_spo2 = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Measurement ID ({self.id})"
    class Meta:
        app_label = 'research'
        db_table = 'measurement'


class Observation(models.Model):
    """
    This table stores paths to multimodal data files.
    """
    visit_occurrence_id = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, db_column='visit_occurrence_id')
    file_type = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    observation_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Observation ID ({self.id})"
    class Meta:
        app_label = 'research'
        db_table = 'observation'


class Labs(models.Model):
    """
    This table records details about a patient's lab orders.
    """
    person_id = models.ForeignKey(Person, on_delete=models.CASCADE, db_column='person_id')
    ordering_date_shifted = models.DateTimeField(null=True, blank=True)
    procedure_id = models.IntegerField()
    procedure_name = models.CharField(max_length=255)
    procedure_code = models.CharField(max_length=255)
    order_type = models.CharField(max_length=255)
    order_status = models.CharField(max_length=255)
    order_proc_deid = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    comp_result_name = models.CharField(max_length=255)
    ord_value = models.CharField(max_length=255, null=True, blank=True)
    ord_num_value = models.FloatField(null=True, blank=True)
    reference_low = models.CharField(max_length=255, null=True, blank=True)
    reference_high = models.CharField(max_length=255, null=True, blank=True)
    reference_unit = models.CharField(max_length=255, null=True, blank=True)
    result_flag = models.CharField(max_length=255, null=True, blank=True)
    lab_status = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Labs ID ({self.id})"
    class Meta:
        app_label = 'research'
        db_table = 'labs'
        verbose_name_plural = 'Labs'