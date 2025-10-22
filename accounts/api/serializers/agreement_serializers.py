from rest_framework import serializers

from accounts.models import Agreement, AgreementType, UserAgreement


class AgreementTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgreementType
        fields = ["id", "name", "description"]


class AgreementSerializer(serializers.ModelSerializer):
    agreement_type = AgreementTypeSerializer(read_only=True)

    class Meta:
        model = Agreement
        fields = [
            "id",
            "agreement_type",
            "title",
            "version",
            "content",
            "document_url",
            "project_name",
            "project_description",
            "created_at",
        ]


class UserAgreementSerializer(serializers.ModelSerializer):
    agreement = AgreementSerializer(read_only=True)
    date_signed = serializers.DateTimeField(source="signed_at", read_only=True)

    class Meta:
        model = UserAgreement
        fields = ["id", "agreement", "date_signed", "is_active"]


class UserAgreementListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing user agreements"""

    agreement_title = serializers.CharField(source="agreement.title", read_only=True)
    agreement_version = serializers.CharField(source="agreement.version", read_only=True)
    agreement_type = serializers.CharField(source="agreement.agreement_type.name", read_only=True)
    project_name = serializers.CharField(source="agreement.project_name", read_only=True)
    project_description = serializers.CharField(
        source="agreement.project_description", read_only=True
    )
    document_url = serializers.URLField(source="agreement.document_url", read_only=True)
    date_signed = serializers.DateTimeField(source="signed_at", read_only=True)

    class Meta:
        model = UserAgreement
        fields = [
            "id",
            "agreement_title",
            "agreement_version",
            "agreement_type",
            "project_name",
            "project_description",
            "document_url",
            "date_signed",
            "is_active",
        ]
