from django.db import models
from .person_provider_models import Person, Provider


class VisitOccurrence(models.Model):
    """
    Records healthcare encounter visits with tier-based access control.

    This model stores comprehensive information about each healthcare encounter,
    including patient and provider associations, visit timing, and access tier.

    Access Control:
        Users can only access visits where their profile.tier.level >= visit.tier_id.
        This implements a hierarchical access control system where higher tiers
        can access data from lower tiers, but not vice versa.

    Relationships:
        - person: The patient for this visit (ForeignKey to Person)
        - provider: The healthcare provider (ForeignKey to Provider)
        - Clinical data models link via visit_occurrence_id:
          * ConditionOccurrence, ProcedureOccurrence, DrugExposure
          * Measurement, Observation, Note

    Database:
        Routed to 'research' database via DatabaseRouter.
        Table: visit_occurrence
    """
    id = models.AutoField(primary_key=True, verbose_name="Visit Occurrence ID")
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    visit_start_date = models.DateField(null=True, blank=True)
    visit_start_time = models.TimeField(null=True, blank=True)
    visit_source_value = models.CharField(max_length=255)
    visit_source_id = models.IntegerField()
    tier_id = models.IntegerField(help_text="Tier level for data access control")

    def __str__(self):
        return f"Visit Occurrence {self.id}"

    class Meta:
        app_label = 'research'
        db_table = 'visit_occurrence'

class Note(models.Model):
    """
    This table stores clinical notes and their associated metadata.
    """
    id = models.AutoField(primary_key=True, verbose_name="Note ID")
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE)
    note_date = models.DateField()
    note_text = models.TextField()
    note_type = models.CharField(max_length=255)
    note_status = models.CharField(max_length=255)

    def __str__(self):
        return f"Note {self.id}"
    
    class Meta:
        app_label = 'research'
        db_table = 'note'


class ConditionOccurrence(models.Model):
    """
    Captures patient conditions and diagnoses linked to healthcare visits.

    Stores diagnostic information including condition codes, primary diagnosis flags,
    and concept mappings for standardized medical terminology.

    Relationships:
        - visit_occurrence: The healthcare visit where this condition was recorded (ForeignKey)
        - Inherits tier-based access control from parent VisitOccurrence

    Database:
        Routed to 'research' database via DatabaseRouter.
        Table: condition_occurrence
    """
    id = models.AutoField(primary_key=True, verbose_name="Condition Occurrence ID")
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE)
    is_primary_dx = models.CharField(max_length=255)
    condition_source_value = models.CharField(max_length=255)
    condition_concept_id = models.IntegerField()
    concept_code = models.CharField(max_length=255)

    def __str__(self):
        return f"Condition Occurrence {self.id}"
    
    class Meta:
        app_label = 'research'
        db_table = 'condition_occurrence'


class DrugExposure(models.Model):
    """
    This table records details about a patient's exposure to specific drugs.
    """
    id = models.AutoField(primary_key=True, verbose_name="Drug Exposure ID")
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE)
    drug_ordering_date = models.DateField(null=True, blank=True)
    drug_exposure_start_datetime = models.DateTimeField(null=True, blank=True)
    drug_exposure_end_datetime = models.DateTimeField(null=True, blank=True)
    description = models.CharField(max_length=255)
    quantity = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Drug Exposure {self.id}"
    
    class Meta:
        app_label = 'research'
        db_table = 'drug_exposure'


class ProcedureOccurrence(models.Model):
    """
    Documents medical procedures performed during healthcare visits.

    Records procedure details including ordering dates, names, descriptions,
    and status indicators for procedures ordered or performed.

    Relationships:
        - visit_occurrence: The healthcare visit where procedure was performed (ForeignKey)
        - Inherits tier-based access control from parent VisitOccurrence

    Database:
        Routed to 'research' database via DatabaseRouter.
        Table: procedure_occurrence
    """
    id = models.AutoField(primary_key=True, verbose_name="Procedure Occurrence ID")
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE)
    procedure_ordering_date = models.DateField()
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    future_or_stand = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Procedure Occurrence {self.id}"
    
    class Meta:
        app_label = 'research'
        db_table = 'procedure_occurrence'


class Measurement(models.Model):
    """
    This table stores quantitative measurements and observations taken during a visit.
    """
    id = models.AutoField(primary_key=True, verbose_name="Measurement ID")
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE)
    bp_systolic = models.IntegerField(null=True, blank=True)
    bp_diastolic = models.IntegerField(null=True, blank=True)
    phys_bp = models.CharField(max_length=255, null=True, blank=True)
    weight_lb = models.FloatField(null=True, blank=True)
    height = models.CharField(max_length=255, null=True, blank=True)
    pulse = models.IntegerField(null=True, blank=True)
    phys_spo2 = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Measurement {self.id}"
    
    class Meta:
        app_label = 'research'
        db_table = 'measurement'


class Observation(models.Model):
    """
    This table stores paths to multimodal data files.
    """
    id = models.AutoField(primary_key=True, verbose_name="Observation ID")
    visit_occurrence = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE)
    file_type = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    observation_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Observation {self.id}"
    
    class Meta:
        app_label = 'research'
        db_table = 'observation'


class Labs(models.Model):
    """
    This table records details about a patient's lab orders.
    """
    id = models.AutoField(primary_key=True, verbose_name="Labs ID")
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
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
        return f"Labs {self.id}"
    
    class Meta:
        app_label = 'research'
        db_table = 'labs'
        verbose_name_plural = 'Labs'