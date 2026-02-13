from rest_framework import serializers

from clinical.models import (
    Department,
    Encounter,
    EncounterFile,
    EncounterSource,
    MultiModalData,
    Patient,
    Provider,
)


class MultiModalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiModalData
        fields = [
            "id",
            "provider_view",
            "patient_view",
            "room_view",
            "audio",
            "transcript",
            "patient_survey",
            "provider_survey",
            "patient_annotation",
            "provider_annotation",
        ]


class EncounterFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EncounterFile
        fields = "__all__"


class EncounterSerializer(serializers.ModelSerializer):
    encounter_source = serializers.PrimaryKeyRelatedField(
        queryset=EncounterSource.objects.using("clinical").all()
    )
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.using("clinical").all()
    )
    provider = serializers.PrimaryKeyRelatedField(queryset=Provider.objects.using("clinical").all())
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.using("clinical").all())
    encounterfile_ids = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, source="files"
    )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.case_id is None:
            date_str = instance.encounter_date_and_time.strftime("%m.%d.%Y")
            representation["case_id"] = f"{instance.provider}_{instance.patient}_{date_str}"
        return representation

    class Meta:
        model = Encounter
        fields = [
            "id",
            "case_id",
            "encounter_source",
            "department",
            "provider",
            "patient",
            "encounter_date_and_time",
            "provider_satisfaction",
            "patient_satisfaction",
            "is_deidentified",
            "is_restricted",
            "type",
            "encounterfile_ids",
            "tier_level",
            "multi_modal_data",
        ]


class PublicEncounterSerializer(serializers.ModelSerializer):
    encounter_source = serializers.StringRelatedField()
    department = serializers.StringRelatedField()
    patient_id = serializers.SerializerMethodField()
    provider_id = serializers.SerializerMethodField()
    multi_modal_data_id = serializers.SerializerMethodField()

    class Meta:
        model = Encounter
        fields = [
            "id",
            "provider_id",
            "patient_id",
            "encounter_source",
            "department",
            "multi_modal_data_id",
            "encounter_date_and_time",
            "patient_satisfaction",
            "provider_satisfaction",
            "is_deidentified",
            "is_restricted",
        ]

    def get_patient_id(self, obj):
        return obj.patient.id if obj.patient else None

    def get_provider_id(self, obj):
        return obj.provider.id if obj.provider else None

    def get_multi_modal_data_id(self, obj):
        return obj.multi_modal_data.id if obj.multi_modal_data else None
