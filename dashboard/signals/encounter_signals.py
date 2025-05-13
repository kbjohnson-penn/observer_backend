from django.db.models.signals import post_save
from django.dispatch import receiver
from dashboard.models import Encounter, MultiModalData, EncounterFile


@receiver(post_save, sender=Encounter)
def link_multimodal_data(sender, instance, created, **kwargs):
    """
    Automatically link a MultiModalData instance to a newly created Encounter.
    """
    if created and not instance.multi_modal_data:
        multimodal_data = MultiModalData.objects.create()
        instance.multi_modal_data = multimodal_data
        instance.case_id = instance.case_id or f'{instance.provider}_{instance.patient}_{instance.encounter_date_and_time.strftime("%m.%d.%Y")}'
        instance.save(update_fields=['multi_modal_data', 'case_id'])


@receiver(post_save, sender=EncounterFile)
def update_multimodal_data(sender, instance, created, **kwargs):
    """
    Update MultiModalData fields based on the EncounterFile type.
    """
    if not instance.encounter or not instance.file_path:
        return

    multimodal_data = instance.encounter.multi_modal_data
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
        setattr(multimodal_data, file_type_mapping[instance.file_type], True)
        multimodal_data.save(
            update_fields=[file_type_mapping[instance.file_type]])
