from rest_framework import serializers
from ..models.profile_models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['date_of_birth', 'phone_number', 'address', 'city', 'state', 'country', 'zip_code', 'bio']