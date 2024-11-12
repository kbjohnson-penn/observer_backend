from django import forms
from ..models import Profile


class CustomDateInput(forms.DateInput):
    input_type = 'date'
    format = '%Y-%m-%d'

    def __init__(self, **kwargs):
        kwargs['format'] = self.format
        super().__init__(**kwargs)


class ProfileForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=CustomDateInput()  # Use CustomDateInput instead of CustomDateTimeInput
    )

    class Meta:
        model = Profile
        fields = ['date_of_birth', 'phone_number', 'address',
                  'city', 'state', 'country', 'zip_code', 'bio']
