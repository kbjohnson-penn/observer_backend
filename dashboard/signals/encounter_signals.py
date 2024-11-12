from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from ..models import Encounter, EncounterSource, Department, EncounterFile, MultiModalData
from ..graph_models import EncounterNode, EncounterSourceNode, DepartmentNode, PatientNode, ProviderNode


@receiver(post_save, sender=EncounterSource)
def create_or_update_encounter_source(sender, instance, created, **kwargs):
    encounter_source_nodes = EncounterSourceNode.nodes.filter(
        django_id=instance.id)
    if created:
        if not encounter_source_nodes:
            EncounterSourceNode(name=instance.name,
                                django_id=instance.id).save()
    else:
        for encounter_source_node in encounter_source_nodes:
            encounter_source_node.name = instance.name
            encounter_source_node.save()


@receiver(post_delete, sender=EncounterSource)
def delete_encounter_source(sender, instance, **kwargs):
    try:
        encounter_source_node = EncounterSourceNode.nodes.get(
            django_id=instance.id)
        encounter_source_node.delete()
    except EncounterSourceNode.DoesNotExist:
        pass


@receiver(post_save, sender=Department)
def create_or_update_department(sender, instance, created, **kwargs):
    department_nodes = DepartmentNode.nodes.filter(django_id=instance.id)
    if created:
        if not department_nodes:
            DepartmentNode(name=instance.name, django_id=instance.id).save()
    else:
        for department_node in department_nodes:
            department_node.name = instance.name
            department_node.save()


@receiver(post_delete, sender=Department)
def delete_department(sender, instance, **kwargs):
    try:
        department_node = DepartmentNode.nodes.get(django_id=instance.id)
        department_node.delete()
    except DepartmentNode.DoesNotExist:
        pass


@receiver(post_save, sender=Encounter)
def create_or_update_encounter_node(sender, instance, created, **kwargs):
    patient = PatientNode.nodes.get_or_none(
        django_id=instance.patient.id) if instance.patient else None
    provider = ProviderNode.nodes.get_or_none(
        django_id=instance.provider.id) if instance.provider else None
    department = DepartmentNode.nodes.get_or_none(
        django_id=instance.department.id) if instance.department else None
    encounter_source = EncounterSourceNode.nodes.get_or_none(
        django_id=instance.encounter_source.id) if instance.encounter_source else None
    encounter_nodes = EncounterNode.nodes.filter(django_id=instance.id)
    if created:
        if not encounter_nodes:
            EncounterNode(
                django_id=instance.id,
                encouter_id_display=f'ENC_{instance.id}',
                encounter_date_and_time=instance.encounter_date_and_time,
                patient_satisfaction=instance.patient_satisfaction,
                provider_satisfaction=instance.provider_satisfaction,
                is_deidentified=instance.is_deidentified,
                is_restricted=instance.is_restricted
            ).save()
    else:
        for encounter_node in encounter_nodes:
            encounter_node.encouter_id_display = f'ENC_{instance.id}'
            encounter_node.encounter_date_and_time = instance.encounter_date_and_time
            encounter_node.patient_satisfaction = instance.patient_satisfaction
            encounter_node.provider_satisfaction = instance.provider_satisfaction
            encounter_node.is_deidentified = instance.is_deidentified
            encounter_node.is_restricted = instance.is_restricted
            encounter_node.save()
    if patient is not None:
        for encounter_node in encounter_nodes:
            encounter_node.patient.disconnect_all()
            encounter_node.patient.connect(patient)
    if provider is not None:
        for encounter_node in encounter_nodes:
            encounter_node.provider.disconnect_all()
            encounter_node.provider.connect(provider)
    if department is not None:
        for encounter_node in encounter_nodes:
            encounter_node.department.disconnect_all()
            encounter_node.department.connect(department)
    if encounter_source is not None:
        for encounter_node in encounter_nodes:
            encounter_node.encounter_source.disconnect_all()
            encounter_node.encounter_source.connect(encounter_source)


@receiver(post_delete, sender=Encounter)
def delete_encounter(sender, instance, **kwargs):
    try:
        encounter = EncounterNode.nodes.get(django_id=instance.id)
        encounter.delete()
    except EncounterNode.DoesNotExist:
        pass


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
