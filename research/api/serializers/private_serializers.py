from rest_framework import serializers

from research.models import (
    AuditLogs,
    ConditionOccurrence,
    DrugExposure,
    Labs,
    Measurement,
    Note,
    Observation,
    PatientSurvey,
    Person,
    ProcedureOccurrence,
    Provider,
    ProviderSurvey,
    VisitOccurrence,
)


class PersonSerializer(serializers.ModelSerializer):
    """Private serializer for Person model - full access for authenticated users."""

    class Meta:
        model = Person
        fields = [
            "id",
            "year_of_birth",
            "gender_source_value",
            "gender_source_concept_id",
            "race_source_value",
            "race_source_concept_id",
            "ethnicity_source_value",
            "ethnicity_source_concept_id",
        ]


class ProviderSerializer(serializers.ModelSerializer):
    """Private serializer for Provider model - full access for authenticated users."""

    class Meta:
        model = Provider
        fields = [
            "id",
            "year_of_birth",
            "gender_source_value",
            "gender_source_concept_id",
            "race_source_value",
            "race_source_concept_id",
            "ethnicity_source_value",
            "ethnicity_source_concept_id",
        ]


class VisitOccurrenceSerializer(serializers.ModelSerializer):
    """Private serializer for VisitOccurrence model - full access with related data."""

    class Meta:
        model = VisitOccurrence
        fields = [
            "id",
            "visit_start_date",
            "visit_start_time",
            "visit_source_value",
            "visit_source_id",
            "tier_id",
            "person_id",
            "provider_id",
        ]


class NoteSerializer(serializers.ModelSerializer):
    """Private serializer for Note model - full access for authenticated users."""

    class Meta:
        model = Note
        fields = [
            "id",
            "note_date",
            "note_text",
            "note_type",
            "note_status",
            "person_id",
            "provider_id",
            "visit_occurrence_id",
        ]


class ConditionOccurrenceSerializer(serializers.ModelSerializer):
    """Private serializer for ConditionOccurrence model - full access for authenticated users."""

    class Meta:
        model = ConditionOccurrence
        fields = [
            "id",
            "is_primary_dx",
            "condition_source_value",
            "condition_concept_id",
            "concept_code",
            "visit_occurrence_id",
        ]


class DrugExposureSerializer(serializers.ModelSerializer):
    """Private serializer for DrugExposure model - full access for authenticated users."""

    class Meta:
        model = DrugExposure
        fields = [
            "id",
            "drug_ordering_date",
            "drug_exposure_start_datetime",
            "drug_exposure_end_datetime",
            "description",
            "quantity",
            "visit_occurrence_id",
        ]


class ProcedureOccurrenceSerializer(serializers.ModelSerializer):
    """Private serializer for ProcedureOccurrence model - full access for authenticated users."""

    class Meta:
        model = ProcedureOccurrence
        fields = [
            "id",
            "procedure_ordering_date",
            "name",
            "description",
            "future_or_stand",
            "visit_occurrence_id",
        ]


class ObservationSerializer(serializers.ModelSerializer):
    """Private serializer for Observation model - full access for authenticated users."""

    class Meta:
        model = Observation
        fields = ["id", "file_type", "file_path", "observation_date", "visit_occurrence_id"]


class MeasurementSerializer(serializers.ModelSerializer):
    """Private serializer for Measurement model - full access for authenticated users."""

    class Meta:
        model = Measurement
        fields = [
            "id",
            "bp_systolic",
            "bp_diastolic",
            "phys_bp",
            "weight_lb",
            "height",
            "pulse",
            "phys_spo2",
            "visit_occurrence_id",
        ]


class AuditLogsSerializer(serializers.ModelSerializer):
    """Private serializer for AuditLogs model - full access for authenticated users."""

    class Meta:
        model = AuditLogs
        fields = [
            "id",
            "access_time",
            "user_id",
            "workstation_id",
            "access_action",
            "metric_id",
            "metric_name",
            "metric_desc",
            "metric_type",
            "metric_group",
            "event_action_type",
            "event_action_subtype",
            "visit_occurrence_id",
        ]


class PatientSurveySerializer(serializers.ModelSerializer):
    """Private serializer for PatientSurvey model - full access for authenticated users."""

    class Meta:
        model = PatientSurvey
        fields = [
            "id",
            "form_1_timestamp",
            "visit_date",
            "patient_overall_health",
            "patient_mental_emotional_health",
            "patient_age",
            "patient_education",
            "overall_satisfaction_scale_1",
            "overall_satisfaction_scale_2",
            "tech_experience_1",
            "tech_experience_2",
            "relationship_with_provider_1",
            "relationship_with_provider_2",
            "hawthorne_1",
            "hawthorne_2",
            "hawthorne_3",
            "hawthorne_4",
            "visit_related_1",
            "visit_related_2",
            "visit_related_3",
            "visit_related_4",
            "visit_related_5",
            "visit_related_6",
            "hawthorne_5",
            "open_ended_interaction",
            "open_ended_change",
            "open_ended_experience",
            "visit_occurrence_id",
        ]


class ProviderSurveySerializer(serializers.ModelSerializer):
    """Private serializer for ProviderSurvey model - full access for authenticated users."""

    class Meta:
        model = ProviderSurvey
        fields = [
            "id",
            "form_1_timestamp",
            "visit_date",
            "years_hcp_experience",
            "tech_experience",
            "communication_method_1",
            "communication_method_2",
            "communication_method_3",
            "communication_method_4",
            "communication_method_5",
            "communication_other",
            "inbasket_messages",
            "overall_satisfaction_scale_1",
            "overall_satisfaction_scale_2",
            "patient_related_1",
            "patient_related_2",
            "patient_related_3",
            "visit_related_1",
            "visit_related_2",
            "visit_related_4",
            "hawthorne_1",
            "hawthorne_2",
            "hawthorne_3",
            "open_ended_1",
            "open_ended_2",
            "visit_occurrence_id",
        ]


class LabsSerializer(serializers.ModelSerializer):
    """Private serializer for Labs model - full access for authenticated users."""

    class Meta:
        model = Labs
        fields = [
            "id",
            "ordering_date_shifted",
            "procedure_id",
            "procedure_name",
            "procedure_code",
            "order_type",
            "order_status",
            "order_proc_deid",
            "description",
            "comp_result_name",
            "ord_value",
            "ord_num_value",
            "reference_low",
            "reference_high",
            "reference_unit",
            "result_flag",
            "lab_status",
            "person_id",
        ]
