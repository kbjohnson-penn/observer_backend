"""
Search serializers for visit filtering with comprehensive data.
Includes visit info, patient demographics, and clinical data counts.
"""

from rest_framework import serializers

from research.models import VisitOccurrence


class VisitSearchResultSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for visit search results.
    Includes visit data, patient demographics, and clinical data counts.
    Optimized for research data browsing and cohort building.
    """

    # Visit fields
    visit_id = serializers.IntegerField(source="id", read_only=True)
    visit_date = serializers.DateField(source="visit_start_date", read_only=True)
    visit_time = serializers.TimeField(source="visit_start_time", read_only=True)
    visit_source = serializers.CharField(source="visit_source_value", read_only=True)
    tier = serializers.IntegerField(source="tier_level", read_only=True)

    # Patient demographics (from related Person model)
    patient_id = serializers.IntegerField(source="person_id", read_only=True)
    patient_year_of_birth = serializers.IntegerField(
        source="person.year_of_birth", allow_null=True, read_only=True
    )
    patient_age = serializers.SerializerMethodField()
    patient_gender = serializers.CharField(
        source="person.gender_source_value", allow_null=True, read_only=True
    )
    patient_race = serializers.CharField(
        source="person.race_source_value", allow_null=True, read_only=True
    )
    patient_ethnicity = serializers.CharField(
        source="person.ethnicity_source_value", allow_null=True, read_only=True
    )

    # Provider info (from related Provider model)
    provider_id = serializers.IntegerField(read_only=True)
    provider_year_of_birth = serializers.IntegerField(
        source="provider.year_of_birth", allow_null=True, read_only=True
    )
    provider_age = serializers.SerializerMethodField()
    provider_gender = serializers.CharField(
        source="provider.gender_source_value", allow_null=True, read_only=True
    )
    provider_race = serializers.CharField(
        source="provider.race_source_value", allow_null=True, read_only=True
    )
    provider_ethnicity = serializers.CharField(
        source="provider.ethnicity_source_value", allow_null=True, read_only=True
    )

    # Clinical data counts (DISABLED - annotate_counts is disabled for performance)
    # Uncomment when precomputed counts are implemented
    # condition_count = serializers.SerializerMethodField()
    # drug_count = serializers.SerializerMethodField()
    # procedure_count = serializers.SerializerMethodField()
    # lab_count = serializers.SerializerMethodField()
    # note_count = serializers.SerializerMethodField()
    # observation_count = serializers.SerializerMethodField()
    # measurement_count = serializers.SerializerMethodField()

    # Boolean flags for quick UI display (DISABLED - based on counts above)
    # has_notes = serializers.SerializerMethodField()
    # has_multimodal = serializers.SerializerMethodField()
    # has_labs = serializers.SerializerMethodField()
    # has_conditions = serializers.SerializerMethodField()

    class Meta:
        model = VisitOccurrence
        fields = [
            # Visit info
            "visit_id",
            "visit_date",
            "visit_time",
            "visit_source",
            "visit_source_id",
            "tier",
            # Patient demographics
            "patient_id",
            "patient_year_of_birth",
            "patient_age",
            "patient_gender",
            "patient_race",
            "patient_ethnicity",
            # Provider info
            "provider_id",
            "provider_year_of_birth",
            "provider_age",
            "provider_gender",
            "provider_race",
            "provider_ethnicity",
            # Clinical data counts (DISABLED - uncomment when implemented)
            # 'condition_count',
            # 'drug_count',
            # 'procedure_count',
            # 'lab_count',
            # 'note_count',
            # 'observation_count',
            # 'measurement_count',
            # Boolean flags (DISABLED - uncomment when implemented)
            # 'has_notes',
            # 'has_multimodal',
            # 'has_labs',
            # 'has_conditions',
        ]

    def get_patient_age(self, obj):
        """
        Calculate patient age at time of visit from year of birth.
        Returns None if year_of_birth or visit_start_date is not available.
        """
        try:
            if obj.person and obj.person.year_of_birth and obj.visit_start_date:
                visit_year = obj.visit_start_date.year
                return visit_year - obj.person.year_of_birth
        except (AttributeError, TypeError):
            pass
        return None

    def get_provider_age(self, obj):
        """
        Calculate provider age at time of visit from year of birth.
        Returns None if year_of_birth or visit_start_date is not available.
        """
        try:
            if obj.provider and obj.provider.year_of_birth and obj.visit_start_date:
                visit_year = obj.visit_start_date.year
                return visit_year - obj.provider.year_of_birth
        except (AttributeError, TypeError):
            pass
        return None

    # Clinical count getters (DISABLED - uncomment when implemented)
    # def get_condition_count(self, obj):
    #     """Get condition count, defaults to 0 if not annotated."""
    #     return getattr(obj, 'condition_count', 0)

    # def get_drug_count(self, obj):
    #     """Get drug count, defaults to 0 if not annotated."""
    #     return getattr(obj, 'drug_count', 0)

    # def get_procedure_count(self, obj):
    #     """Get procedure count, defaults to 0 if not annotated."""
    #     return getattr(obj, 'procedure_count', 0)

    # def get_lab_count(self, obj):
    #     """Get lab count, defaults to 0 if not annotated."""
    #     return getattr(obj, 'lab_count', 0)

    # def get_note_count(self, obj):
    #     """Get note count, defaults to 0 if not annotated."""
    #     return getattr(obj, 'note_count', 0)

    # def get_observation_count(self, obj):
    #     """Get observation count, defaults to 0 if not annotated."""
    #     return getattr(obj, 'observation_count', 0)

    # def get_measurement_count(self, obj):
    #     """Get measurement count, defaults to 0 if not annotated."""
    #     return getattr(obj, 'measurement_count', 0)

    # Boolean flag getters (DISABLED - uncomment when implemented)
    # def get_has_notes(self, obj):
    #     """Check if visit has clinical notes."""
    #     return getattr(obj, 'note_count', 0) > 0

    # def get_has_multimodal(self, obj):
    #     """Check if visit has multimodal data (observations)."""
    #     return getattr(obj, 'observation_count', 0) > 0

    # def get_has_labs(self, obj):
    #     """Check if patient has lab results."""
    #     return getattr(obj, 'lab_count', 0) > 0

    # def get_has_conditions(self, obj):
    #     """Check if visit has documented conditions."""
    #     return getattr(obj, 'condition_count', 0) > 0
