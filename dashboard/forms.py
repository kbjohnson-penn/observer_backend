from django import forms
from .models import Encounter, Patient, Provider
from datetime import datetime

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
