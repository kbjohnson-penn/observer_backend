import logging
from django import forms
from dashboard.models import EncounterFile, Encounter
from dashboard.storage_backend import AzureDataLakeStorage
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

DATETIME_FORMAT = '%Y-%m-%dT%H:%M'
FILE_NAME_ERROR = "File name must be present."
FILE_TYPE_ERROR = "File type must be present."
ENCOUNTER_SOURCE_ERROR = "Encounter source must be present."
FILE_NOT_EXIST_ERROR = "The file '{file_name}' does not exist at '{file_path}' in the storage account."


class CustomDateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'
    format = DATETIME_FORMAT

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

        file_name = cleaned_data.get('file_name')
        file_type = cleaned_data.get('file_type')
        encounter = self.instance.encounter

        if not encounter:
            raise ValidationError("The encounter must be set for the file.")

        encounter_source = encounter.encounter_source

        logger.debug(
            f"file_name: {file_name}, file_type: {file_type}, encounter_source: {encounter_source}")

        if not file_name:
            raise ValidationError(FILE_NAME_ERROR)
        if not file_type:
            raise ValidationError(FILE_TYPE_ERROR)
        if not encounter_source:
            raise ValidationError(ENCOUNTER_SOURCE_ERROR)

        file_path = f"{encounter_source.name}/{encounter}/{file_type}/{file_name}"

        logger.info(f"Checking existence of file: {file_path}")

        if not storage.file_exists(file_path):
            logger.warning(
                f"File '{file_name}' does not exist in storage path '{file_path}'.")
            raise ValidationError(FILE_NOT_EXIST_ERROR.format(
                file_name=file_name, file_path=file_path))

        self.instance.file_path = file_path

        return cleaned_data

    def save(self, commit=True):
        return super().save(commit=commit)
