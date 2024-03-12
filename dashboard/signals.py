from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Encounter, AnonymizedMapping
from .graph_models import AnonymizedPatient, AnonymizedProvider, AnonymizedEncounter
import uuid

@receiver(post_save, sender=Encounter)
def create_anonymized_mapping(sender, instance, created, **kwargs):
    if created:
        anonymized_encounter_id = uuid.uuid4()
        anonymized_patient_id = uuid.uuid4()
        anonymized_provider_id = uuid.uuid4()

        patient_node = AnonymizedPatient(anonymized_id=str(anonymized_patient_id)).save()
        provider_node = AnonymizedProvider(anonymized_id=str(anonymized_provider_id)).save()
        encounter_node = AnonymizedEncounter(uid=str(anonymized_encounter_id), encounter_date=instance.encounter_date).save()

        encounter_node.patient.connect(patient_node)
        encounter_node.provider.connect(provider_node)

        AnonymizedMapping.objects.create(
            encounter=instance, 
            anonymized_encounter_id=anonymized_encounter_id, 
            anonymized_patient_id=anonymized_patient_id, 
            anonymized_provider_id=anonymized_provider_id
        )