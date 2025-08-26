from django.db import models
from .person_provider_models import Person, Provider


class VisitOccurrence(models.Model):
    """
    This table records details about each healthcare encounter or visit a person has.
    """
    person_id = models.ForeignKey('Person', on_delete=models.CASCADE, db_column='person_id')
    provider_id = models.ForeignKey('Provider', on_delete=models.CASCADE, db_column='provider_id')
    visit_start_date = models.DateField()
    visit_start_time = models.TimeField()
    visit_source_value = models.TextField()
    visit_source_id = models.IntegerField()
    tier_id = models.IntegerField(help_text="Tier level for data access control")

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
    note_type = models.TextField()
    note_status = models.TextField()

    class Meta:
        app_label = 'research'
        db_table = 'note'


class ConditionOccurrence(models.Model):
    """
    This table captures information about conditions or diagnoses recorded for a patient.
    """
    visit_occurrence_id = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, db_column='visit_occurrence_id')
    is_primary_dx = models.TextField()
    condition_source_value = models.TextField()
    condition_concept_id = models.IntegerField()
    concept_code = models.TextField()

    class Meta:
        app_label = 'research'
        db_table = 'condition_occurrence'


class DrugExposure(models.Model):
    """
    This table records details about a patient's exposure to specific drugs.
    """
    visit_occurrence_id = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, db_column='visit_occurrence_id')
    drug_ordering_date = models.DateField()
    drug_exposure_start_datetime = models.DateTimeField()
    drug_exposure_end_datetime = models.DateTimeField()
    description = models.TextField()
    quantity = models.TextField()

    class Meta:
        app_label = 'research'
        db_table = 'drug_exposure'


class ProcedureOccurrence(models.Model):
    """
    This table documents procedures performed on patients.
    """
    visit_occurrence_id = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, db_column='visit_occurrence_id')
    procedure_ordering_date = models.DateField()
    name = models.TextField()
    description = models.TextField()
    future_or_stand = models.TextField()

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
    phys_bp = models.TextField(blank=True)
    weight_lb = models.FloatField(null=True, blank=True)
    height = models.TextField(blank=True)
    pulse = models.IntegerField(null=True, blank=True)
    phys_spo2 = models.IntegerField(null=True, blank=True)

    class Meta:
        app_label = 'research'
        db_table = 'measurement'


class Observation(models.Model):
    """
    This table stores paths to multimodal data files.
    """
    visit_occurrence_id = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, db_column='visit_occurrence_id')
    file_type = models.TextField()
    file_path = models.TextField()
    observation_date = models.DateField()

    class Meta:
        app_label = 'research'
        db_table = 'observation'