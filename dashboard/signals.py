from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Patient, Provider, Department, Encounter, MultiModalDataPath
from .graph_models import PatientNode, ProviderNode, DepartmentNode, EncounterNode, MultiModalDataPathNode


@receiver(post_save, sender=Patient)
def create_or_update_patient(sender, instance, created, **kwargs):
    if created:
        if not PatientNode.nodes.filter(patient_id=instance.patient_id):
            PatientNode(
                patient_id=instance.patient_id,
                date_of_birth=instance.date_of_birth,
                sex=instance.sex,
                race=instance.race,
                ethnicity=instance.ethnicity
            ).save()
    else:
        patient_node = PatientNode.nodes.get(patient_id=instance.patient_id)
        patient_node.date_of_birth = instance.date_of_birth
        patient_node.sex = instance.sex
        patient_node.race = instance.race
        patient_node.ethnicity = instance.ethnicity
        patient_node.save()


@receiver(post_delete, sender=Patient)
def delete_patient(sender, instance, **kwargs):
    try:
        patient_node = PatientNode.nodes.get(patient_id=instance.patient_id)
        patient_node.delete()
    except PatientNode.DoesNotExist:
        pass


@receiver(post_save, sender=Provider)
def create_or_update_provider(sender, instance, created, **kwargs):
    if created:
        if not ProviderNode.nodes.filter(provider_id=instance.provider_id):
            ProviderNode(
                provider_id=instance.provider_id,
                date_of_birth=instance.date_of_birth,
                sex=instance.sex,
                race=instance.race,
                ethnicity=instance.ethnicity
            ).save()
    else:
        provider_node = ProviderNode.nodes.get(
            provider_id=instance.provider_id)
        provider_node.date_of_birth = instance.date_of_birth
        provider_node.sex = instance.sex
        provider_node.race = instance.race
        provider_node.ethnicity = instance.ethnicity
        provider_node.save()


@receiver(post_delete, sender=Provider)
def delete_provider(sender, instance, **kwargs):
    try:
        provider_node = ProviderNode.nodes.get(
            provider_id=instance.provider_id)
        provider_node.delete()
    except ProviderNode.DoesNotExist:
        pass


@receiver(post_save, sender=Department)
def create_or_update_department(sender, instance, created, **kwargs):
    if created:
        if not DepartmentNode.nodes.filter(name=instance.name):
            DepartmentNode(name=instance.name).save()
    else:
        department_node = DepartmentNode.nodes.get(name=instance.name)
        department_node.name = instance.name
        department_node.save()


@receiver(post_delete, sender=Department)
def delete_department(sender, instance, **kwargs):
    try:
        department_node = DepartmentNode.nodes.get(name=instance.name)
        department_node.delete()
    except DepartmentNode.DoesNotExist:
        pass


@receiver(post_save, sender=MultiModalDataPath)
def create_or_update_multi_modal_data_path(sender, instance, created, **kwargs):
    if created:
        if not MultiModalDataPathNode.nodes.filter(multi_modal_data_id=instance.multi_modal_data_id):
            MultiModalDataPathNode(
                multi_modal_data_id=instance.multi_modal_data_id,
                provider_view=instance.provider_view,
                patient_view=instance.patient_view,
                room_view=instance.room_view,
                audio=instance.audio,
                transcript=instance.transcript,
                patient_survey=instance.patient_survey,
                provider_survey=instance.provider_survey
            ).save()
    else:
        multi_modal_data_path_node = MultiModalDataPathNode.nodes.get(
            multi_modal_data_id=instance.multi_modal_data_id)
        multi_modal_data_path_node.provider_view = instance.provider_view
        multi_modal_data_path_node.patient_view = instance.patient_view
        multi_modal_data_path_node.room_view = instance.room_view
        multi_modal_data_path_node.audio = instance.audio
        multi_modal_data_path_node.transcript = instance.transcript
        multi_modal_data_path_node.patient_survey = instance.patient_survey
        multi_modal_data_path_node.provider_survey = instance.provider_survey
        multi_modal_data_path_node.save()


@receiver(post_delete, sender=MultiModalDataPath)
def delete_multi_modal_data_path(sender, instance, **kwargs):
    try:
        multi_modal_data_path_node = MultiModalDataPathNode.nodes.get(
            multi_modal_data_id=instance.multi_modal_data_id)
        multi_modal_data_path_node.delete()
    except MultiModalDataPathNode.DoesNotExist:
        pass


@receiver(post_save, sender=Encounter)
def create_or_update_encounter(sender, instance, created, **kwargs):
    # Fetch related objects in bulk
    patient = PatientNode.nodes.get_or_none(
        patient_id=instance.patient.patient_id) if instance.patient else None
    provider = ProviderNode.nodes.get_or_none(
        provider_id=instance.provider.provider_id) if instance.provider else None
    department = DepartmentNode.nodes.get_or_none(
        name=instance.department.name) if instance.department else None
    multi_modal_data = MultiModalDataPathNode.nodes.get_or_none(
        multi_modal_data_id=instance.multi_modal_data.multi_modal_data_id) if instance.multi_modal_data else None

    # Create or update EncounterNode
    if created:
        encounter = EncounterNode(
            case_id=instance.case_id,
            encounter_date_and_time=instance.encounter_date_and_time,
            patient_satisfaction=instance.patient_satisfaction,
            provider_satisfaction=instance.provider_satisfaction,
            is_deidentified=instance.is_deidentified,
            is_restricted=instance.is_restricted
        ).save()
    else:
        encounter = EncounterNode.nodes.get(case_id=instance.case_id)
        encounter.encounter_date_and_time = instance.encounter_date_and_time
        encounter.patient_satisfaction = instance.patient_satisfaction
        encounter.provider_satisfaction = instance.provider_satisfaction
        encounter.is_deidentified = instance.is_deidentified
        encounter.is_restricted = instance.is_restricted
        encounter.save()

    # Connect EncounterNode to related objects
    if patient is not None:
        encounter.patient.connect(patient)
    if provider is not None:
        encounter.provider.connect(provider)
    if department is not None:
        encounter.department.connect(department)
    if multi_modal_data is not None:
        encounter.data_paths.connect(multi_modal_data)


@receiver(post_delete, sender=Encounter)
def delete_encounter(sender, instance, **kwargs):
    try:
        encounter = EncounterNode.nodes.get(case_id=instance.case_id)
        encounter.delete()
    except EncounterNode.DoesNotExist:
        pass
