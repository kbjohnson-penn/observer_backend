from django.contrib import admin
from django import forms
from ..models import Encounter, EncounterFile, Department, Patient, Provider
from ..forms import EncounterForm, PatientForm, ProviderForm, EncounterFileForm


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
    readonly_fields = ['file_path']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['encounter_source'].widget = forms.HiddenInput()
        return form


class EncounterAdmin(admin.ModelAdmin):
    form = EncounterForm
    inlines = [EncounterFileInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['encounter_source'].widget = forms.HiddenInput()
        form.base_fields['multi_modal_data'].widget = forms.HiddenInput()
        return form

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()


admin.site.register(Patient, PatientAdmin)
admin.site.register(Provider, ProviderAdmin)
admin.site.register(Department)
admin.site.register(Encounter, EncounterAdmin)
