from django.utils import timezone
from clinical.models import EncounterSource, Patient, Provider, MultiModalData
from shared.constants import (
    SIMCENTER_PATIENT_ID_LOWER_LIMIT, 
    SIMCENTER_PATIENT_ID_UPPER_LIMIT,
    SIMCENTER_PROVIDER_ID_LOWER_LIMIT, 
    SIMCENTER_PROVIDER_ID_UPPER_LIMIT
)


class EncounterService:
    """Service class for handling Encounter-related business logic."""
    
    @classmethod
    def prepare_encounter_for_save(cls, encounter):
        """
        Prepare an encounter instance for saving by handling all business logic.
        This method should be called before saving the encounter.
        """
        cls._ensure_encounter_source(encounter)
        cls._ensure_timezone_aware_datetime(encounter)
        cls._ensure_multi_modal_data(encounter)
        cls._ensure_case_id(encounter)
        
        if encounter.type == 'simcenter':
            cls._handle_simcenter_logic(encounter)
    
    @classmethod
    def _ensure_encounter_source(cls, encounter):
        """Create encounter source if it doesn't exist."""
        if not encounter.encounter_source:
            encounter.encounter_source, _ = EncounterSource.objects.using('clinical').get_or_create(
                name=encounter.type.capitalize()
            )
    
    @classmethod
    def _ensure_timezone_aware_datetime(cls, encounter):
        """Ensure the encounter datetime is timezone-aware."""
        if encounter.encounter_date_and_time and timezone.is_naive(encounter.encounter_date_and_time):
            encounter.encounter_date_and_time = timezone.make_aware(
                encounter.encounter_date_and_time
            )
    
    @classmethod
    def _ensure_multi_modal_data(cls, encounter):
        """Create MultiModalData if it doesn't exist."""
        if not encounter.multi_modal_data:
            encounter.multi_modal_data = MultiModalData.objects.using('clinical').create()
    
    @classmethod
    def _ensure_case_id(cls, encounter):
        """Generate case_id if not provided."""
        if not encounter.case_id and encounter.provider and encounter.patient:
            formatted_date = encounter.encounter_date_and_time.strftime("%m.%d.%Y")
            encounter.case_id = f'{encounter.provider}_{encounter.patient}_{formatted_date}'
    
    @classmethod
    def _handle_simcenter_logic(cls, encounter):
        """Handle simcenter-specific patient and provider creation logic."""
        # Preserve existing patient/provider if this is an update
        if encounter.pk is not None:
            cls._preserve_existing_relations(encounter)
        
        # Create new patient if needed
        if not encounter.patient:
            encounter.patient = cls._create_simcenter_patient()
        
        # Create new provider if needed
        if not encounter.provider:
            encounter.provider = cls._create_simcenter_provider()
    
    @classmethod
    def _preserve_existing_relations(cls, encounter):
        """Preserve existing patient/provider relationships during updates."""
        try:
            from clinical.models import Encounter
            existing = Encounter.objects.using('clinical').get(pk=encounter.pk)
            if existing.patient and not encounter.patient:
                encounter.patient = existing.patient
            if existing.provider and not encounter.provider:
                encounter.provider = existing.provider
        except Encounter.DoesNotExist:
            pass
    
    @classmethod
    def _create_simcenter_patient(cls):
        """Create a new patient with auto-generated ID for simcenter encounters."""
        highest_patient = Patient.objects.using('clinical').filter(
            patient_id__gte=SIMCENTER_PATIENT_ID_LOWER_LIMIT,
            patient_id__lt=SIMCENTER_PATIENT_ID_UPPER_LIMIT
        ).order_by('-patient_id').first()
        
        new_id = (SIMCENTER_PATIENT_ID_LOWER_LIMIT 
                 if not highest_patient 
                 else highest_patient.patient_id + 1)
        
        # Validate we haven't exceeded the range
        if new_id >= SIMCENTER_PATIENT_ID_UPPER_LIMIT:
            raise ValueError(
                f"Simcenter patient ID range exhausted. "
                f"Cannot create patient with ID >= {SIMCENTER_PATIENT_ID_UPPER_LIMIT}"
            )
        
        return Patient.objects.using('clinical').create(patient_id=new_id)
    
    @classmethod
    def _create_simcenter_provider(cls):
        """Create a new provider with auto-generated ID for simcenter encounters."""
        highest_provider = Provider.objects.using('clinical').filter(
            provider_id__gte=SIMCENTER_PROVIDER_ID_LOWER_LIMIT,
            provider_id__lt=SIMCENTER_PROVIDER_ID_UPPER_LIMIT
        ).order_by('-provider_id').first()
        
        new_id = (SIMCENTER_PROVIDER_ID_LOWER_LIMIT 
                 if not highest_provider 
                 else highest_provider.provider_id + 1)
        
        # Validate we haven't exceeded the range
        if new_id >= SIMCENTER_PROVIDER_ID_UPPER_LIMIT:
            raise ValueError(
                f"Simcenter provider ID range exhausted. "
                f"Cannot create provider with ID >= {SIMCENTER_PROVIDER_ID_UPPER_LIMIT}"
            )
        
        return Provider.objects.using('clinical').create(provider_id=new_id)