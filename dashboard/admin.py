from django import forms
from django.contrib import admin
from .models import Patient, Provider, Department, MultiModalDataPath, Encounter, EncounterSimCenter, EncounterRIAS
from .forms import EncounterForm, PatientForm, ProviderForm

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


class EncounterAdmin(admin.ModelAdmin):
    form = EncounterForm

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

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['encounter_source'].widget = forms.HiddenInput()
        form.base_fields['provider'].widget = forms.HiddenInput()
        form.base_fields['patient'].widget = forms.HiddenInput()
        return form


class EncounterRIASAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['encounter_source'].widget = forms.HiddenInput()
        form.base_fields['provider'].widget = forms.HiddenInput()
        form.base_fields['patient'].widget = forms.HiddenInput()
        return form


admin.site.register(Patient, PatientAdmin)
admin.site.register(Provider, ProviderAdmin)
admin.site.register(Department)
admin.site.register(MultiModalDataPath)
admin.site.register(Encounter, EncounterAdmin)
admin.site.register(EncounterSimCenter, EncounterSimCenterAdmin)
admin.site.register(EncounterRIAS, EncounterRIASAdmin)
