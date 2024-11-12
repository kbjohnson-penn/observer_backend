from django import forms
from ..models import Provider


class CustomDateInput(forms.DateInput):
    input_type = 'date'
    format = '%Y-%m-%d'

    def __init__(self, **kwargs):
        kwargs['format'] = self.format
        super().__init__(**kwargs)


class ProviderForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=CustomDateInput()
    )

    class Meta:
        model = Provider
        fields = '__all__'
