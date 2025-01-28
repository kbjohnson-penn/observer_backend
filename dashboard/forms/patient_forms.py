from django import forms
from dashboard.models import Patient
from dashboard.custom_widgets import CustomDateInput


class PatientForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=CustomDateInput()
    )

    class Meta:
        model = Patient
        fields = '__all__'
