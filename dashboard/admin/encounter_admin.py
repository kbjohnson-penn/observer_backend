from django.contrib import admin
from django import forms
from dashboard.models import Encounter, EncounterFile, Department, Patient, Provider, Tier
from dashboard.forms import EncounterForm, PatientForm, ProviderForm, EncounterFileForm
from dashboard.constants import SIMCENTER_PATIENT_ID_LOWER_LIMIT, SIMCENTER_PATIENT_ID_UPPER_LIMIT, SIMCENTER_PROVIDER_ID_LOWER_LIMIT, SIMCENTER_PROVIDER_ID_UPPER_LIMIT

PATIENT_ID_EXCLUDE_RANGE = (
    SIMCENTER_PATIENT_ID_LOWER_LIMIT, SIMCENTER_PATIENT_ID_UPPER_LIMIT)
PROVIDER_ID_EXCLUDE_RANGE = (
    SIMCENTER_PROVIDER_ID_LOWER_LIMIT, SIMCENTER_PROVIDER_ID_UPPER_LIMIT)


class ExcludeIdRangeMixin:
    exclude_id_range = None
    exclude_field = None

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(**{f"{self.exclude_field}__range": self.exclude_id_range})


class PatientAdmin(ExcludeIdRangeMixin, admin.ModelAdmin):
    form = PatientForm
    exclude_field = 'patient_id'
    exclude_id_range = PATIENT_ID_EXCLUDE_RANGE


class ProviderAdmin(ExcludeIdRangeMixin, admin.ModelAdmin):
    form = ProviderForm
    exclude_field = 'provider_id'
    exclude_id_range = PROVIDER_ID_EXCLUDE_RANGE


class EncounterFileInline(admin.TabularInline):
    model = EncounterFile
    form = EncounterFileForm
    extra = 1
    readonly_fields = ['file_path']

    def customize_form(self, form):
        form.base_fields['encounter_source'].widget = forms.HiddenInput()
        return form

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return self.customize_form(form)


class EncounterAdmin(admin.ModelAdmin):
    form = EncounterForm
    inlines = [EncounterFileInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "patient":
            kwargs["queryset"] = Patient.objects.exclude(
                patient_id__range=PATIENT_ID_EXCLUDE_RANGE)
        if db_field.name == "provider":
            kwargs["queryset"] = Provider.objects.exclude(
                provider_id__range=PROVIDER_ID_EXCLUDE_RANGE)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def customize_form(self, form):
        form.base_fields['encounter_source'].widget = forms.HiddenInput()
        form.base_fields['multi_modal_data'].widget = forms.HiddenInput()
        return form

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return self.customize_form(form)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()


admin.site.register(Patient, PatientAdmin)
admin.site.register(Provider, ProviderAdmin)
admin.site.register(Department)
admin.site.register(Encounter, EncounterAdmin)
admin.site.register(Tier)
