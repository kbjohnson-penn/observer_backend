from django.contrib import admin
from .models import (
    Person, Provider, VisitOccurrence, Note, ConditionOccurrence,
    DrugExposure, ProcedureOccurrence, Measurement, Observation,
    PatientSurvey, ProviderSurvey, Concept, AuditLogs, Labs
)


class ResearchModelAdmin(admin.ModelAdmin):
    """Base admin class for research models with multi-database support."""
    using = 'research'
    
    def save_model(self, request, obj, form, change):
        obj.save(using=self.using)
    
    def delete_model(self, request, obj):
        obj.delete(using=self.using)
    
    def get_queryset(self, request):
        return super().get_queryset(request).using(self.using)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return super().formfield_for_foreignkey(
            db_field, request, using=self.using, **kwargs
        )
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        return super().formfield_for_manytomany(
            db_field, request, using=self.using, **kwargs
        )


# Register your models here.
@admin.register(Person)
class PersonAdmin(ResearchModelAdmin):
    list_display = ['id', 'year_of_birth', 'gender_source_value', 'race_source_value']
    list_filter = ['gender_source_concept_id', 'race_source_concept_id']
    search_fields = ['gender_source_value', 'race_source_value']
    ordering = ['id']

@admin.register(Provider)
class ProviderAdmin(ResearchModelAdmin):
    list_display = ['id', 'year_of_birth', 'gender_source_value', 'race_source_value']
    list_filter = ['gender_source_concept_id', 'race_source_concept_id']
    search_fields = ['gender_source_value', 'race_source_value']
    ordering = ['id']

@admin.register(VisitOccurrence)
class VisitOccurrenceAdmin(ResearchModelAdmin):
    list_display = ['id', 'person', 'provider', 'visit_start_date', 'visit_start_time']
    list_filter = ['visit_start_date']
    search_fields = ['visit_source_value']
    date_hierarchy = 'visit_start_date'
    raw_id_fields = ['person', 'provider']
    ordering = ['-visit_start_date']

@admin.register(Concept)
class ConceptAdmin(ResearchModelAdmin):
    list_display = ['concept_id', 'concept_name', 'vocabulary_name', 'concept_code', 'domain_name']
    list_filter = ['vocabulary_name', 'domain_name']
    search_fields = ['concept_name', 'concept_code', 'concept_id']
    ordering = ['concept_name']

@admin.register(Note)
class NoteAdmin(ResearchModelAdmin):
    list_display = ['id', 'person', 'note_date', 'note_type']
    list_filter = ['note_date', 'note_type', 'note_status']
    search_fields = ['note_text', 'note_type']
    date_hierarchy = 'note_date'
    raw_id_fields = ['person', 'provider', 'visit_occurrence']
    ordering = ['-note_date']

@admin.register(ConditionOccurrence)
class ConditionOccurrenceAdmin(ResearchModelAdmin):
    list_display = ['id', 'visit_occurrence', 'condition_concept_id', 'is_primary_dx']
    list_filter = ['is_primary_dx']
    search_fields = ['condition_source_value', 'concept_code']
    raw_id_fields = ['visit_occurrence']
    ordering = ['-id']

@admin.register(DrugExposure)
class DrugExposureAdmin(ResearchModelAdmin):
    list_display = ['id', 'visit_occurrence', 'drug_ordering_date', 'description']
    list_filter = ['drug_ordering_date', 'drug_exposure_start_datetime']
    search_fields = ['description', 'quantity']
    date_hierarchy = 'drug_ordering_date'
    raw_id_fields = ['visit_occurrence']
    ordering = ['-drug_ordering_date']

@admin.register(ProcedureOccurrence)
class ProcedureOccurrenceAdmin(ResearchModelAdmin):
    list_display = ['id', 'visit_occurrence', 'procedure_ordering_date', 'name']
    list_filter = ['procedure_ordering_date', 'future_or_stand']
    search_fields = ['name', 'description']
    date_hierarchy = 'procedure_ordering_date'
    raw_id_fields = ['visit_occurrence']
    ordering = ['-procedure_ordering_date']

@admin.register(Measurement)
class MeasurementAdmin(ResearchModelAdmin):
    list_display = ['id', 'visit_occurrence', 'bp_systolic', 'bp_diastolic', 'weight_lb', 'pulse']
    list_filter = ['phys_bp']
    search_fields = ['height']
    raw_id_fields = ['visit_occurrence']
    ordering = ['-id']

@admin.register(Observation)
class ObservationAdmin(ResearchModelAdmin):
    list_display = ['id', 'visit_occurrence', 'file_type', 'observation_date']
    list_filter = ['file_type', 'observation_date']
    search_fields = ['file_path']
    date_hierarchy = 'observation_date'
    raw_id_fields = ['visit_occurrence']
    ordering = ['-observation_date']

@admin.register(PatientSurvey)
class PatientSurveyAdmin(ResearchModelAdmin):
    list_display = ['id', 'visit_occurrence', 'visit_date', 'patient_overall_health']
    list_filter = ['patient_overall_health', 'patient_mental_emotional_health']
    search_fields = ['visit_date', 'open_ended_interaction', 'open_ended_change']
    raw_id_fields = ['visit_occurrence']
    ordering = ['-id']

@admin.register(ProviderSurvey)
class ProviderSurveyAdmin(ResearchModelAdmin):
    list_display = ['id', 'visit_occurrence', 'visit_date', 'years_hcp_experience']
    list_filter = ['years_hcp_experience', 'tech_experience']
    search_fields = ['visit_date', 'open_ended_1', 'open_ended_2']
    raw_id_fields = ['visit_occurrence']
    ordering = ['-id']

@admin.register(AuditLogs)
class AuditLogsAdmin(ResearchModelAdmin):
    list_display = ['id', 'access_time', 'user_id', 'access_action', 'metric_name']
    list_filter = ['access_action', 'metric_type', 'event_action_type']
    search_fields = ['user_id', 'workstation_id', 'metric_name']
    raw_id_fields = ['visit_occurrence']
    ordering = ['-id']
    readonly_fields = ['id', 'access_time', 'user_id', 'workstation_id', 'access_action',
                      'metric_id', 'metric_name', 'metric_desc', 'metric_type', 'metric_group',
                      'event_action_type', 'event_action_subtype']

@admin.register(Labs)
class LabsAdmin(ResearchModelAdmin):
    list_display = ['id', 'person', 'ordering_date_shifted', 'description']
    list_filter = ['order_type', 'order_status']
    search_fields = ['procedure_name', 'description', 'lab_status']
    raw_id_fields = ['person']
    ordering = ['-id']