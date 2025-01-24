from django import forms
from ..models import Provider
from ..custom_widgets import CustomDateInput


class ProviderForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=CustomDateInput()
    )

    class Meta:
        model = Provider
        fields = '__all__'
