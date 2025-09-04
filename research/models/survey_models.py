from django.db import models
from .clinical_models import VisitOccurrence


class PatientSurvey(models.Model):
    """
    This table stores patient survey responses related to their healthcare visit experiences.
    """
    visit_occurrence_id = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, db_column='visit_occurrence_id')
    form_1_timestamp = models.DateTimeField(null=True)
    visit_date = models.DateField(null=True)
    patient_overall_health = models.FloatField(null=True, blank=True)
    patient_mental_emotional_health = models.FloatField(null=True, blank=True)
    patient_age = models.FloatField(null=True, blank=True)
    patient_education = models.FloatField(null=True, blank=True)
    overall_satisfaction_scale_1 = models.FloatField(null=True, blank=True)
    overall_satisfaction_scale_2 = models.FloatField(null=True, blank=True)
    tech_experience_1 = models.FloatField(null=True, blank=True)
    tech_experience_2 = models.FloatField(null=True, blank=True)
    relationship_with_provider_1 = models.FloatField(null=True, blank=True)
    relationship_with_provider_2 = models.FloatField(null=True, blank=True)
    hawthorne_1 = models.FloatField(null=True, blank=True)
    hawthorne_2 = models.FloatField(null=True, blank=True)
    hawthorne_3 = models.FloatField(null=True, blank=True)
    hawthorne_4 = models.FloatField(null=True, blank=True)
    visit_related_1 = models.FloatField(null=True, blank=True)
    visit_related_2 = models.FloatField(null=True, blank=True)
    visit_related_3 = models.FloatField(null=True, blank=True)
    visit_related_4 = models.FloatField(null=True, blank=True)
    visit_related_5 = models.FloatField(null=True, blank=True)
    visit_related_6 = models.FloatField(null=True, blank=True)
    hawthorne_5 = models.FloatField(null=True, blank=True)
    open_ended_interaction = models.TextField(null=True, blank=True)
    open_ended_change = models.TextField(null=True, blank=True)
    open_ended_experience = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Patient Survey ID ({self.id})"
    class Meta:
        app_label = 'research'
        db_table = 'patient_survey'


class ProviderSurvey(models.Model):
    """
    This table stores responses from healthcare providers regarding their experiences 
    and satisfaction with patient visits, including communication preferences and technology use.
    """
    visit_occurrence_id = models.ForeignKey(VisitOccurrence, on_delete=models.CASCADE, db_column='visit_occurrence_id')
    form_1_timestamp = models.DateTimeField(null=True)
    visit_date = models.DateField(null=True)
    years_hcp_experience = models.IntegerField(null=True, blank=True)
    tech_experience = models.IntegerField(null=True, blank=True)
    communication_method_1 = models.IntegerField(null=True, blank=True)
    communication_method_2 = models.IntegerField(null=True, blank=True)
    communication_method_3 = models.IntegerField(null=True, blank=True)
    communication_method_4 = models.IntegerField(null=True, blank=True)
    communication_method_5 = models.IntegerField(null=True, blank=True)
    communication_other = models.CharField(max_length=255, null=True, blank=True)
    inbasket_messages = models.IntegerField(null=True, blank=True)
    overall_satisfaction_scale_1 = models.IntegerField(null=True, blank=True)
    overall_satisfaction_scale_2 = models.IntegerField(null=True, blank=True)
    patient_related_1 = models.IntegerField(null=True, blank=True)
    patient_related_2 = models.IntegerField(null=True, blank=True)
    patient_related_3 = models.IntegerField(null=True, blank=True)
    visit_related_1 = models.IntegerField(null=True, blank=True)
    visit_related_2 = models.IntegerField(null=True, blank=True)
    visit_related_4 = models.IntegerField(null=True, blank=True)
    hawthorne_1 = models.IntegerField(null=True, blank=True)
    hawthorne_2 = models.IntegerField(null=True, blank=True)
    hawthorne_3 = models.IntegerField(null=True, blank=True)
    open_ended_1 = models.TextField(null=True, blank=True)
    open_ended_2 = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Provider Survey ID ({self.id})"
    class Meta:
        app_label = 'research'
        db_table = 'provider_survey'