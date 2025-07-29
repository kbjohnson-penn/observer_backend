from django.db import models


class EncounterManager(models.Manager):
    """Custom manager for Encounter model with common query patterns."""
    
    def with_related(self):
        """Return encounters with commonly accessed related objects."""
        return self.select_related(
            'patient', 'provider', 'department', 'encounter_source', 'multi_modal_data'
        ).prefetch_related('files')
    
    def by_type(self, encounter_type):
        """Filter encounters by type."""
        return self.filter(type=encounter_type)
    
    def simcenter(self):
        """Return only simcenter encounters."""
        return self.by_type('simcenter')
    
    def deidentified_only(self):
        """Return only de-identified encounters."""
        return self.filter(is_deidentified=True)
    
    def restricted_only(self):
        """Return only restricted encounters."""
        return self.filter(is_restricted=True)


class PatientManager(models.Manager):
    """Custom manager for Patient model with common query patterns."""
    
    def simcenter_range(self):
        """Return patients within the simcenter ID range."""
        from shared.constants import SIMCENTER_PATIENT_ID_LOWER_LIMIT, SIMCENTER_PATIENT_ID_UPPER_LIMIT
        return self.filter(
            patient_id__gte=SIMCENTER_PATIENT_ID_LOWER_LIMIT,
            patient_id__lt=SIMCENTER_PATIENT_ID_UPPER_LIMIT
        )
    
    def with_encounters(self):
        """Return patients with their encounters prefetched."""
        return self.prefetch_related('encounter_set')


class ProviderManager(models.Manager):
    """Custom manager for Provider model with common query patterns."""
    
    def simcenter_range(self):
        """Return providers within the simcenter ID range."""
        from shared.constants import SIMCENTER_PROVIDER_ID_LOWER_LIMIT, SIMCENTER_PROVIDER_ID_UPPER_LIMIT
        return self.filter(
            provider_id__gte=SIMCENTER_PROVIDER_ID_LOWER_LIMIT,
            provider_id__lt=SIMCENTER_PROVIDER_ID_UPPER_LIMIT
        )
    
    def with_encounters(self):
        """Return providers with their encounters prefetched."""
        return self.prefetch_related('encounter_set')


class EncounterFileManager(models.Manager):
    """Custom manager for EncounterFile model with common query patterns."""
    
    def by_file_type(self, file_type):
        """Filter files by type."""
        return self.filter(file_type=file_type)
    
    def with_encounter(self):
        """Return files with their associated encounter."""
        return self.select_related('encounter')
    
    def for_encounter(self, encounter):
        """Return all files for a specific encounter."""
        return self.filter(encounter=encounter)