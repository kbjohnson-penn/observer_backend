from django.contrib import admin
from .models import Patient, Provider, Department, Encounter, EncounterFile, MultiModalData, EncounterSource


class ClinicalModelAdmin(admin.ModelAdmin):
    """Base admin class for clinical models with multi-database support."""
    using = 'clinical'

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
@admin.register(Patient)
class PatientAdmin(ClinicalModelAdmin):
    list_display = ['patient_id', 'first_name', 'last_name', 'sex', 'timestamp']
    list_filter = ['sex', 'race', 'ethnicity', 'timestamp']
    search_fields = ['patient_id', 'first_name', 'last_name']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']

@admin.register(Provider)
class ProviderAdmin(ClinicalModelAdmin):
    list_display = ['provider_id', 'first_name', 'last_name', 'sex', 'timestamp']
    list_filter = ['sex', 'race', 'ethnicity', 'timestamp']
    search_fields = ['provider_id', 'first_name', 'last_name']
    date_hierarchy = 'timestamp'
    ordering = ['provider_id']

@admin.register(Department)
class DepartmentAdmin(ClinicalModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']

@admin.register(EncounterSource)
class EncounterSourceAdmin(ClinicalModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']

@admin.register(Encounter)
class EncounterAdmin(ClinicalModelAdmin):
    list_display = ['id', 'csn_number', 'patient', 'provider', 'department', 'type', 'tier_id', 'encounter_date_and_time']
    list_filter = ['type', 'department', 'encounter_date_and_time', 'tier_id', 'is_deidentified', 'is_restricted']
    search_fields = ['csn_number', 'case_id', 'patient__patient_id', 'provider__provider_id']
    date_hierarchy = 'encounter_date_and_time'
    raw_id_fields = ['patient', 'provider', 'multi_modal_data']
    ordering = ['-encounter_date_and_time']

@admin.register(EncounterFile)
class EncounterFileAdmin(ClinicalModelAdmin):
    list_display = ['encounter', 'file_type', 'file_name', 'timestamp']
    list_filter = ['file_type', 'timestamp']
    search_fields = ['file_name', 'file_path', 'encounter__csn_number']
    date_hierarchy = 'timestamp'
    raw_id_fields = ['encounter']
    ordering = ['-timestamp']

@admin.register(MultiModalData)
class MultiModalDataAdmin(ClinicalModelAdmin):
    list_display = ['id', 'provider_view', 'patient_view', 'room_view', 'audio', 'transcript', 'timestamp']
    list_filter = ['provider_view', 'patient_view', 'room_view', 'audio', 'transcript', 'timestamp']
    search_fields = []
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
