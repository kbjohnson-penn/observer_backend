from django import forms
from django.contrib import admin
from .models import Patient, Provider, Department, MultiModalDataPath, Encounter, EncounterSimCenter, EncounterRIAS, EncounterFile
from .forms import EncounterForm, PatientForm, ProviderForm, EncounterFileForm


class PatientAdmin(admin.ModelAdmin):
    form = PatientForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(patient_id__range=(100000, 999999))


class ProviderAdmin(admin.ModelAdmin):
    form = ProviderForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(provider_id__range=(100000, 999999))


class EncounterFileInline(admin.TabularInline):
    model = EncounterFile
    form = EncounterFileForm
    extra = 1
    fields = ['file_type', 'file', 'file_path', 'delete_file']
    readonly_fields = ['file_path']

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['delete_file'].widget = forms.CheckboxInput()
        return formset


class EncounterAdmin(admin.ModelAdmin):
    form = EncounterForm
    inlines = [EncounterFileInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "patient":
            kwargs["queryset"] = Patient.objects.exclude(
                patient_id__range=(100000, 999999))
        if db_field.name == "provider":
            kwargs["queryset"] = Provider.objects.exclude(
                provider_id__range=(100000, 999999))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['encounter_source'].widget = forms.HiddenInput()
        return form


class EncounterSimCenterAdmin(admin.ModelAdmin):
    form = EncounterForm
    inlines = [EncounterFileInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['encounter_source'].widget = forms.HiddenInput()
        form.base_fields['provider'].widget = forms.HiddenInput()
        form.base_fields['patient'].widget = forms.HiddenInput()
        return form


class EncounterRIASAdmin(admin.ModelAdmin):
    inlines = [EncounterFileInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['encounter_source'].widget = forms.HiddenInput()
        form.base_fields['provider'].widget = forms.HiddenInput()
        form.base_fields['patient'].widget = forms.HiddenInput()
        return form


admin.site.register(Patient, PatientAdmin)
admin.site.register(Provider, ProviderAdmin)
admin.site.register(Department)
admin.site.register(Encounter, EncounterAdmin)
admin.site.register(EncounterSimCenter, EncounterSimCenterAdmin)
admin.site.register(EncounterRIAS, EncounterRIASAdmin)
