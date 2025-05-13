from django import forms
from dashboard.models import Provider
from dashboard.custom_widgets import CustomDateInput


class ProviderForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=CustomDateInput()
    )

    class Meta:
        model = Provider
        fields = '__all__'
