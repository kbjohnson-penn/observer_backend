from django import forms
from ..models import Profile
from ..custom_widgets import CustomDateInput


class ProfileForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=CustomDateInput()
    )

    class Meta:
        model = Profile
        fields = ['date_of_birth', 'phone_number', 'address',
                  'city', 'state', 'country', 'zip_code', 'bio', 'organization', 'tier']
