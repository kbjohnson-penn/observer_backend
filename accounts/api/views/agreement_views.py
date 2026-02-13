from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.api.serializers.agreement_serializers import (
    AgreementSerializer,
    AgreementTypeSerializer,
    UserAgreementListSerializer,
)
from accounts.models import Agreement, AgreementType, UserAgreement


class UserAgreementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving user's signed agreements.
    Provides list, retrieve, and custom actions.
    """

    serializer_class = UserAgreementListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return agreements for the current user only"""
        return (
            UserAgreement.objects.using("accounts")
            .filter(user=self.request.user, is_active=True)
            .select_related("agreement", "agreement__agreement_type")
            .order_by("-signed_at")
        )

    @action(detail=False, methods=["get"])
    def grouped(self, request):
        """
        Get user agreements grouped by type (for settings page).
        Returns data in the format expected by the frontend.
        """
        user_agreements = self.get_queryset()

        # Group by agreement type
        agreements_by_type = {}

        for user_agreement in user_agreements:
            agreement_type = user_agreement.agreement.agreement_type.name

            if agreement_type not in agreements_by_type:
                agreements_by_type[agreement_type] = []

            # Format the data to match frontend expectations
            agreement_data = {
                "id": user_agreement.id,
                "date": user_agreement.signed_at.strftime("%b. %d, %Y"),
                "agreement": f"{user_agreement.agreement.title} {user_agreement.agreement.version}",
                "project": user_agreement.agreement.project_description
                or user_agreement.agreement.project_name,
                "viewUrl": user_agreement.agreement.document_url,
                "version": user_agreement.agreement.version,
                "name": user_agreement.agreement.title,
            }

            agreements_by_type[agreement_type].append(agreement_data)

        # Format response to match frontend structure
        response_data = {}

        # Data Use Agreements
        if "Data Use Agreement" in agreements_by_type:
            response_data["data_use_agreements"] = agreements_by_type["Data Use Agreement"]
        else:
            response_data["data_use_agreements"] = []

        # Code of Conduct
        if "Code of Conduct" in agreements_by_type:
            response_data["code_of_conduct"] = agreements_by_type["Code of Conduct"]
        else:
            response_data["code_of_conduct"] = []

        # Other agreement types
        for agreement_type, agreements in agreements_by_type.items():
            if agreement_type not in ["Data Use Agreement", "Code of Conduct"]:
                key = agreement_type.lower().replace(" ", "_")
                response_data[key] = agreements

        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def types(self, request):
        """Get all available agreement types"""
        agreement_types = AgreementType.objects.using("accounts").all()
        serializer = AgreementTypeSerializer(agreement_types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AgreementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving available agreements.
    Allows users to view agreements before signing them.
    CSRF protection enabled - frontend must include CSRF token for state-changing operations.
    """

    serializer_class = AgreementSerializer
    permission_classes = [IsAuthenticated]
    queryset = (
        Agreement.objects.using("accounts").filter(is_active=True).order_by("-created_at", "id")
    )

    @action(detail=False, methods=["get"])
    def by_type(self, request):
        """Get agreements grouped by type"""
        agreement_type = request.query_params.get("type")
        if agreement_type:
            agreements = self.queryset.filter(agreement_type__name=agreement_type)
        else:
            agreements = self.queryset.all()

        serializer = self.get_serializer(agreements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
