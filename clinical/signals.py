from django.db.models.signals import post_save
from django.dispatch import receiver
from clinical.models import EncounterFile


@receiver(post_save, sender=EncounterFile)  
def update_multimodal_data(sender, instance, created, using, **kwargs):
    """
    Update MultiModalData fields based on the EncounterFile type.
    """
    if not instance.encounter or not instance.file_path:
        return

    multimodal_data = instance.encounter.multi_modal_data
    if not multimodal_data:
        return
        
    file_type_mapping = {
        'provider_view': 'provider_view',
        'patient_view': 'patient_view', 
        'room_view': 'room_view',
        'audio': 'audio',
        'transcript': 'transcript',
        'patient_survey': 'patient_survey',
        'provider_survey': 'provider_survey',
        'patient_annotation': 'patient_annotation',
        'provider_annotation': 'provider_annotation',
        'rias_transcript': 'rias_transcript',
        'rias_codes': 'rias_codes',
    }

    if instance.file_type in file_type_mapping:
        field_name = file_type_mapping[instance.file_type]
        setattr(multimodal_data, field_name, True)
        multimodal_data.save(using=using, update_fields=[field_name])