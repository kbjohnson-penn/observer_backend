from django import forms
from ..models import Patient
from ..custom_widgets import CustomDateInput


class PatientForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=CustomDateInput()
    )

    class Meta:
        model = Patient
        fields = '__all__'
