from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from datetime import date
from ..models import Patient
from ..graph_models import PatientNode


def calculate_year_of_birth_for_max_age(born):
    today = date.today()
    age = today.year - born.year - \
        ((today.month, today.day) < (born.month, born.day))
    if age > 89:
        return today.year - 89
    return born.year


@receiver(post_save, sender=Patient)
def create_or_update_patient(sender, instance, created, **kwargs):
    if created:
        PatientNode(
            patient_id=instance.patient_id,
            patient_id_display=f'PT{instance.patient_id}',
            year_of_birth=calculate_year_of_birth_for_max_age(
                instance.date_of_birth) if instance.date_of_birth else None,
            sex=instance.sex,
            race=instance.race,
            ethnicity=instance.ethnicity,
            django_id=instance.id
        ).save()
    else:
        patient_node = PatientNode.nodes.get(django_id=instance.id)
        patient_node.patient_id = instance.patient_id
        patient_node.patient_id_display = f'PT{instance.patient_id}'
        patient_node.year_of_birth = calculate_year_of_birth_for_max_age(
            instance.date_of_birth) if instance.date_of_birth else None
        patient_node.sex = instance.sex
        patient_node.race = instance.race
        patient_node.ethnicity = instance.ethnicity
        patient_node.save()


@receiver(post_delete, sender=Patient)
def delete_patient(sender, instance, **kwargs):
    try:
        patient_node = PatientNode.nodes.get(django_id=instance.id)
        patient_node.delete()
    except PatientNode.DoesNotExist:
        pass
