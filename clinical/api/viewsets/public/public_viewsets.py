from clinical.api.serializers import (
    MultiModalDataSerializer,
    PublicDepartmentSerializer,
    PublicEncounterSerializer,
    PublicEncounterSourceSerializer,
    PublicPatientSerializer,
    PublicProviderSerializer,
)
from clinical.models import (
    Department,
    Encounter,
    EncounterSource,
    MultiModalData,
    Patient,
    Provider,
)
from shared.api.permissions import BasePublicReadOnlyViewSet


class PublicEncounterSourceViewSet(BasePublicReadOnlyViewSet):
    """
    Read-only viewset for public access to encounter source data from clinical database.
    """

    serializer_class = PublicEncounterSourceSerializer

    def get_queryset(self):
        """Ensure queries use the clinical database."""
        return EncounterSource.objects.using("clinical").all()


class PublicPatientViewSet(BasePublicReadOnlyViewSet):
    """
    Read-only viewset for public access to patient data from clinical database.
    """

    serializer_class = PublicPatientSerializer

    def get_queryset(self):
        """Ensure queries use the clinical database."""
        return Patient.objects.using("clinical").all()


class PublicProviderViewSet(BasePublicReadOnlyViewSet):
    """
    Read-only viewset for public access to provider data from clinical database.
    """

    serializer_class = PublicProviderSerializer

    def get_queryset(self):
        """Ensure queries use the clinical database."""
        return Provider.objects.using("clinical").all()


class PublicEncounterViewSet(BasePublicReadOnlyViewSet):
    """
    Read-only viewset for public access to encounter data from clinical database.
    """

    serializer_class = PublicEncounterSerializer

    def get_queryset(self):
        """Ensure queries use the clinical database with optimized relations."""
        return (
            Encounter.objects.using("clinical")
            .select_related(
                "patient", "provider", "encounter_source", "department", "multi_modal_data"
            )
            .all()
        )


class PublicDepartmentViewSet(BasePublicReadOnlyViewSet):
    """
    Read-only viewset for public access to department data from clinical database.
    """

    serializer_class = PublicDepartmentSerializer

    def get_queryset(self):
        """Ensure queries use the clinical database."""
        return Department.objects.using("clinical").all()


class PublicMultiModalDataViewSet(BasePublicReadOnlyViewSet):
    """
    Read-only viewset for public access to multimodal data from clinical database.
    """

    serializer_class = MultiModalDataSerializer

    def get_queryset(self):
        """Ensure queries use the clinical database."""
        return MultiModalData.objects.using("clinical").all()
