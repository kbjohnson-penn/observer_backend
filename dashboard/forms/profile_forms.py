from django import forms
from dashboard.models import Profile
from dashboard.custom_widgets import CustomDateInput


class ProfileForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=CustomDateInput()
    )

    class Meta:
        model = Profile
        fields = ['date_of_birth', 'phone_number', 'address_1', 'address_2',
                  'city', 'state', 'country', 'zip_code', 'bio', 'organization', 'tier']
