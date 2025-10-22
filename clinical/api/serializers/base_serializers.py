from datetime import date

from rest_framework import serializers

from shared.utils import calculate_age


class PersonSerializer(serializers.ModelSerializer):
    """
    A base serializer for person-like models (Patient, Provider) that
    includes shared de-identification and data consistency logic.
    """

    year_of_birth = serializers.SerializerMethodField()

    def get_year_of_birth(self, instance):
        """
        Calculates the year of birth, capping the age at 89 for de-identification.
        """
        age = calculate_age(instance.date_of_birth)
        if age is None:
            return None
        if age > 89:
            # Per HIPAA, ages over 89 are aggregated to protect identity.
            max_year_of_birth = date.today().year - 90
            return str(max_year_of_birth)
        return str(instance.date_of_birth.year) if instance.date_of_birth else None

    def to_representation(self, instance):
        """
        Ensures that 'race', 'sex', and 'ethnicity' fields default to 'UN' (Unknown)
        instead of null for API consistency.
        """
        rep = super().to_representation(instance)
        for field in ["race", "sex", "ethnicity"]:
            # Ensure sensitive fields have a default value if not set.
            rep[field] = rep.get(field, "UN")
        return rep
