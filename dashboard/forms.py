import logging
from django import forms
from .models import Encounter, Patient, Provider, EncounterFile, EncounterSource
from .storage_backend import AzureDataLakeStorage
from django.core.exceptions import ValidationError


logger = logging.getLogger(__name__)

class CustomDateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'
    format = '%Y-%m-%dT%H:%M'

    def __init__(self, **kwargs):
        kwargs['format'] = self.format
        super().__init__(**kwargs)


class CustomDateInput(forms.DateInput):
    input_type = 'date'
    format = '%Y-%m-%d'

    def __init__(self, **kwargs):
        kwargs['format'] = self.format
        super().__init__(**kwargs)


class EncounterForm(forms.ModelForm):
    encounter_date_and_time = forms.DateTimeField(
        widget=CustomDateTimeInput()
    )

    class Meta:
        model = Encounter
        fields = '__all__'


class PatientForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=CustomDateInput()
    )

    class Meta:
        model = Patient
        fields = '__all__'


class ProviderForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=CustomDateInput()
    )

    class Meta:
        model = Provider
        fields = '__all__'


class EncounterFileForm(forms.ModelForm):
    file_name = forms.CharField(required=False)

    class Meta:
        model = EncounterFile
        fields = ['file_type', 'file_name']

    def clean(self):
        cleaned_data = super().clean()
        storage = AzureDataLakeStorage()

        # Extract file_name and file_type from cleaned_data
        file_name = cleaned_data.get('file_name')
        file_type = cleaned_data.get('file_type')
        encounter = self.instance.encounter
        encounter_sim_center = self.instance.encounter_sim_center
        encounter_rias = self.instance.encounter_rias
        encounter_source = self.instance.encounter_source

        # Ensure encounter_source is set before validation
        if not encounter_source:
            if encounter:
                encounter_source, created = EncounterSource.objects.get_or_create(name='Clinic')
            elif encounter_sim_center:
                encounter_source, created = EncounterSource.objects.get_or_create(name='SimCenter')
            elif encounter_rias:
                encounter_source, created = EncounterSource.objects.get_or_create(name='RIAS')
            else:
                raise ValidationError("The encounter must be set for the file.")
            self.instance.encounter_source = encounter_source
        
        logger.debug(f"file_name: {file_name}, file_type: {file_type}, encounter_source: {encounter_source}")

        if not file_name:
            raise ValidationError("File name must be present.")
        if not file_type:
            raise ValidationError("File type must be present.")
        if not encounter_source:
            raise ValidationError("Encounter source must be present.")

        # Dynamically construct the file path based on the encounter source name
        if encounter:
            file_path = f"{encounter_source.name}/{encounter}/{file_type}/{file_name}"
        elif encounter_sim_center:
            file_path = f"{encounter_source.name}/{encounter_sim_center}/{file_type}/{file_name}"
        elif encounter_rias:
            file_path = f"{encounter_source.name}/{encounter_rias}/{file_type}/{file_name}"
        else:
            raise ValidationError("Encounter, EncounterSimCenter, or EncounterRias must be present.")
        
        logger.info(f"Checking existence of file: {file_path}")
        
        if not storage.file_exists(file_path):
            logger.warning(f"File '{file_name}' does not exist in storage path '{file_path}'.")
            raise ValidationError(
                f"The file '{file_name}' does not exist at '{file_path}' in the storage account."
            )
        self.instance.file_path = file_path  # Save the valid path if exists

        return cleaned_data

    def save(self, commit=True):
        return super().save(commit=commit)
