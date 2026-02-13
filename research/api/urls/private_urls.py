from django.urls import path

from rest_framework.routers import DefaultRouter

from research.api.viewsets.private.audit_logs_viewset import AuditLogsViewSet
from research.api.viewsets.private.cohort_data_viewset import CohortDataViewSet
from research.api.viewsets.private.condition_occurrence_viewset import ConditionOccurrenceViewSet
from research.api.viewsets.private.drug_exposure_viewset import DrugExposureViewSet
from research.api.viewsets.private.export_viewset import ExportViewSet
from research.api.viewsets.private.filter_options_viewset import FilterOptionsViewSet
from research.api.viewsets.private.labs_viewset import LabViewSet
from research.api.viewsets.private.measurement_viewset import MeasurementViewSet
from research.api.viewsets.private.note_viewset import NoteViewSet
from research.api.viewsets.private.observation_viewset import ObservationViewSet
from research.api.viewsets.private.patient_survey_viewset import PatientSurveyViewSet
from research.api.viewsets.private.person_viewset import PersonViewSet
from research.api.viewsets.private.procedure_occurrence_viewset import ProcedureOccurrenceViewSet
from research.api.viewsets.private.provider_survey_viewset import ProviderSurveyViewSet
from research.api.viewsets.private.provider_viewset import ProviderViewSet
from research.api.viewsets.private.visit_occurrence_viewset import VisitOccurrenceViewSet
from research.api.viewsets.private.visit_search_viewset import VisitSearchViewSet

router = DefaultRouter()

# Register all research model viewsets
router.register(r"persons", PersonViewSet, basename="v1-research-person")
router.register(r"providers", ProviderViewSet, basename="v1-research-provider")
router.register(r"visits", VisitOccurrenceViewSet, basename="v1-research-visit")
router.register(r"notes", NoteViewSet, basename="v1-research-note")
router.register(
    r"condition-occurrences",
    ConditionOccurrenceViewSet,
    basename="v1-research-condition-occurrence",
)
router.register(r"drug-exposures", DrugExposureViewSet, basename="v1-research-drug-exposure")
router.register(
    r"procedure-occurrences",
    ProcedureOccurrenceViewSet,
    basename="v1-research-procedure-occurrence",
)
router.register(r"observations", ObservationViewSet, basename="v1-research-observation")
router.register(r"measurements", MeasurementViewSet, basename="v1-research-measurement")
router.register(r"audit-logs", AuditLogsViewSet, basename="v1-research-audit-log")
router.register(r"patient-surveys", PatientSurveyViewSet, basename="v1-research-patient-survey")
router.register(r"provider-surveys", ProviderSurveyViewSet, basename="v1-research-provider-survey")
router.register(r"filter-options", FilterOptionsViewSet, basename="v1-research-filter-options")
router.register(r"visits-search", VisitSearchViewSet, basename="v1-research-visit-search")
router.register(r"labs", LabViewSet, basename="v1-research-lab")
router.register(r"export", ExportViewSet, basename="v1-research-export")

# Custom URL patterns for non-standard endpoints
urlpatterns = [
    # Cohort data endpoint - fetch all OMOP tables filtered by cohort
    path(
        "cohorts/<int:pk>/data/",
        CohortDataViewSet.as_view({"get": "retrieve"}),
        name="cohort-data",
    ),
]

# Add router URLs
urlpatterns += router.urls
