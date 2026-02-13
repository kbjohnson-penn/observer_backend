from clinical.models import Provider

from .base_serializers import PersonSerializer


class PublicProviderSerializer(PersonSerializer):
    class Meta:
        model = Provider
        fields = ["id", "year_of_birth", "sex", "race", "ethnicity"]


class ProviderSerializer(PersonSerializer):
    class Meta:
        model = Provider
        fields = ["id", "provider_id", "year_of_birth", "sex", "race", "ethnicity"]
