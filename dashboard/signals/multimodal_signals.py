from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models.encounter_models import Encounter, EncounterFile, MultiModalData


@receiver(post_save, sender=Encounter)
def link_multimodal_data(sender, instance, created, **kwargs):
    if created and not instance.multi_modal_data:
        multimodal_data = MultiModalData.objects.create()
        instance.multi_modal_data = multimodal_data
        instance.save()


@receiver(post_save, sender=EncounterFile)
def update_multimodal_data(sender, instance, created, **kwargs):
    if instance.encounter:
        multimodal_data = instance.encounter.multi_modal_data
    else:
        return
    if instance.file_type == 'provider_view' and instance.file_path != '':
        multimodal_data.provider_view = True
    elif instance.file_type == 'patient_view' and instance.file_path != '':
        multimodal_data.patient_view = True
    elif instance.file_type == 'room_view' and instance.file_path != '':
        multimodal_data.room_view = True
    elif instance.file_type == 'audio' and instance.file_path != '':
        multimodal_data.audio = True
    elif instance.file_type == 'transcript' and instance.file_path != '':
        multimodal_data.transcript = True
    elif instance.file_type == 'patient_survey' and instance.file_path != '':
        multimodal_data.patient_survey = True
    elif instance.file_type == 'provider_survey' and instance.file_path != '':
        multimodal_data.provider_survey = True
    elif instance.file_type == 'patient_annotation' and instance.file_path != '':
        multimodal_data.patient_annotation = True
    elif instance.file_type == 'provider_annotation' and instance.file_path != '':
        multimodal_data.provider_annotation = True
    elif instance.file_type == 'rias_transcript' and instance.file_path != '':
        multimodal_data.rias_transcript = True
    elif instance.file_type == 'rias_codes' and instance.file_path != '':
        multimodal_data.rias_codes = True
    multimodal_data.save()
