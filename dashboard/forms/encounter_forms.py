import logging
from django import forms
from ..models import EncounterFile, Encounter
from ..storage_backend import AzureDataLakeStorage
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class CustomDateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'
    format = '%Y-%m-%dT%H:%M'

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

        # Ensure encounter is set before validation
        if not encounter:
            raise ValidationError("The encounter must be set for the file.")

        encounter_source = encounter.encounter_source

        logger.debug(
            f"file_name: {file_name}, file_type: {file_type}, encounter_source: {encounter_source}")

        if not file_name:
            raise ValidationError("File name must be present.")
        if not file_type:
            raise ValidationError("File type must be present.")
        if not encounter_source:
            raise ValidationError("Encounter source must be present.")

        # Dynamically construct the file path based on the encounter source name
        file_path = f"{encounter_source.name}/{encounter}/{file_type}/{file_name}"

        logger.info(f"Checking existence of file: {file_path}")

        if not storage.file_exists(file_path):
            logger.warning(
                f"File '{file_name}' does not exist in storage path '{file_path}'.")
            raise ValidationError(
                f"The file '{file_name}' does not exist at '{file_path}' in the storage account."
            )
        self.instance.file_path = file_path  # Save the valid path if exists

        return cleaned_data

    def save(self, commit=True):
        return super().save(commit=commit)
