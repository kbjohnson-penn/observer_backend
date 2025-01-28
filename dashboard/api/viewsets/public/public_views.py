from dashboard.models import Patient, Provider, Department, MultiModalData, Encounter, EncounterSource
from dashboard.api.serializers import PublicPatientSerializer, PublicProviderSerializer, PublicEncounterSerializer, PublicDepartmentSerializer, MultiModalDataSerializer, PublicEncounterSourceSerializer
from .base import BasePublicReadOnlyViewSet


class PublicEncounterSourceViewSet(BasePublicReadOnlyViewSet):
    """
    Read-only viewset for public access to encounter source data.
    """
    queryset = EncounterSource.objects.all()
    serializer_class = PublicEncounterSourceSerializer


class PublicPatientViewSet(BasePublicReadOnlyViewSet):
    """
    Read-only viewset for public access to patient data.
    """
    queryset = Patient.objects.all()
    serializer_class = PublicPatientSerializer


class PublicProviderViewSet(BasePublicReadOnlyViewSet):
    """
    Read-only viewset for public access to provider data.
    """
    queryset = Provider.objects.all()
    serializer_class = PublicProviderSerializer


class PublicEncounterViewSet(BasePublicReadOnlyViewSet):
    """
    Read-only viewset for public access to encounter data.
    """
    queryset = Encounter.objects.all()
    serializer_class = PublicEncounterSerializer


class PublicDepartmentViewSet(BasePublicReadOnlyViewSet):
    """
    Read-only viewset for public access to department data.
    """
    queryset = Department.objects.all()
    serializer_class = PublicDepartmentSerializer


class PublicMultiModalDataViewSet(BasePublicReadOnlyViewSet):
    """
    Read-only viewset for public access to multimodal data.
    """
    queryset = MultiModalData.objects.all()
    serializer_class = MultiModalDataSerializer
