import logging
from django import forms
from .models import Encounter, Patient, Provider, EncounterFile
from .storage_backend import AzureDataLakeStorage

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
    file = forms.FileField(required=False)
    file_path = forms.CharField(widget=forms.TextInput(
        attrs={'readonly': 'readonly'}), required=False)
    delete_file = forms.BooleanField(required=False, initial=False)

    class Meta:
        model = EncounterFile
        fields = ['file_type', 'file', 'file_path', 'delete_file']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            storage = AzureDataLakeStorage()
            if self.instance.file_path and storage.file_exists(self.instance.file_path):
                self.fields['file_path'].initial = self.instance.file_path

    def save(self, commit=True):
        instance = super().save(commit=False)
        file = self.cleaned_data.get('file')
        delete_file = self.cleaned_data.get('delete_file')
        storage = AzureDataLakeStorage()

        if delete_file and instance.file_path:
            logger.info(f"Deleting file: {instance.file_path}")
            try:
                storage.delete_from_storage(instance.file_path)
                instance.delete()
                return None
            except Exception as e:
                logger.error(f"Failed to delete file '{instance.file_path}': {str(e)}")
                raise

        if file:
            if instance.file_path:
                logger.info(f"Deleting existing file before saving new one: {instance.file_path}")
                try:
                    storage.delete_from_storage(instance.file_path)
                except Exception as e:
                    logger.error(f"Failed to delete existing file '{instance.file_path}': {str(e)}")
                    raise
            try:
                if instance.encounter:
                    instance.file_path = storage.save_to_storage(
                        file, instance.encounter, instance.file_type)
                elif instance.encounter_sim_center:
                    instance.file_path = storage.save_to_storage(
                        file, instance.encounter_sim_center, instance.file_type)
                    pass
                elif instance.encounter_rias:
                    instance.file_path = storage.save_to_storage(
                        file, instance.encounter_rias, instance.file_type)
                    pass
            except Exception as e:
                logger.error(f"Failed to save new file '{file.name}': {str(e)}")
                raise

        if commit:
            instance.save()
        return instance
