from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Patient, Provider, Department, Encounter, EncounterSource, EncounterSimCenter, EncounterRIAS
from .graph_models import PatientNode, ProviderNode, DepartmentNode, EncounterNode, EncounterSourceNode, EncounterSimCenterNode, EncounterRIASNode
from datetime import date


def calculate_year_of_birth_for_max_age(born):
    today = date.today()
    age = today.year - born.year - \
        ((today.month, today.day) < (born.month, born.day))
    if age > 89:
        # If the age is greater than 89, calculate and return the year of birth for age 89
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
        patient_node = PatientNode.nodes.get(
            django_id=instance.id)
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
        patient_node = PatientNode.nodes.get(
            django_id=instance.id)
        patient_node.delete()
    except PatientNode.DoesNotExist:
        pass


@receiver(post_save, sender=Provider)
def create_or_update_provider(sender, instance, created, **kwargs):

    if created:
        ProviderNode(
            provider_id=instance.provider_id,
            provider_id_display=f'PR{instance.provider_id}',
            year_of_birth=calculate_year_of_birth_for_max_age(
                instance.date_of_birth) if instance.date_of_birth else None,
            sex=instance.sex,
            race=instance.race,
            ethnicity=instance.ethnicity,
            django_id=instance.id
        ).save()
    else:
        provider_node = ProviderNode.nodes.get(
            django_id=instance.id)
        provider_node.provider_id = instance.provider_id
        provider_node.provider_id_display = f'PR{instance.provider_id}'
        provider_node.year_of_birth = calculate_year_of_birth_for_max_age(
            instance.date_of_birth) if instance.date_of_birth else None
        provider_node.sex = instance.sex
        provider_node.race = instance.race
        provider_node.ethnicity = instance.ethnicity
        provider_node.save()


@receiver(post_delete, sender=Provider)
def delete_provider(sender, instance, **kwargs):
    try:
        provider_node = ProviderNode.nodes.get(
            django_id=instance.id)
        provider_node.delete()
    except ProviderNode.DoesNotExist:
        pass


@receiver(post_delete, sender=Provider)
def delete_provider(sender, instance, **kwargs):
    try:
        provider_node = ProviderNode.nodes.get(
            provider_id=instance.provider_id)
        provider_node.delete()
    except ProviderNode.DoesNotExist:
        pass


@receiver(post_save, sender=EncounterSource)
def create_or_update_encounter_source(sender, instance, created, **kwargs):
    encounter_source_nodes = EncounterSourceNode.nodes.filter(
        django_id=instance.id)

    if created:
        if not encounter_source_nodes:
            EncounterSourceNode(
                name=instance.name,
                django_id=instance.id
            ).save()
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
            DepartmentNode(
                name=instance.name,
                django_id=instance.id
            ).save()
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


@receiver(post_save, sender=EncounterSimCenter)
def create_or_update_encounter_sim_center_node(sender, instance, created, **kwargs):
    department = DepartmentNode.nodes.get_or_none(
        django_id=instance.department.id) if instance.department else None
    encounter_source = EncounterSourceNode.nodes.get_or_none(
        django_id=instance.encounter_source.id) if instance.encounter_source else None
    patient = PatientNode.nodes.get_or_none(
        django_id=instance.patient.id) if instance.patient else None
    provider = ProviderNode.nodes.get_or_none(
        django_id=instance.provider.id) if instance.provider else None

    encounter_sim_center_nodes = EncounterSimCenterNode.nodes.filter(
        django_id=instance.id)

    if created:
        if not encounter_sim_center_nodes:
            EncounterSimCenterNode(
                django_id=instance.id,
                encounter_id_display=f'ENS_{instance.id}',
                case_id=instance.case_id,
                encounter_date_and_time=instance.encounter_date_and_time,
                is_deidentified=instance.is_deidentified,
                is_restricted=instance.is_restricted
            ).save()
    else:
        for encounter_sim_center_node in encounter_sim_center_nodes:
            encounter_sim_center_node.encounter_id_display = f'ENS_{instance.id}'
            encounter_sim_center_node.case_id = instance.case_id
            encounter_sim_center_node.encounter_date_and_time = instance.encounter_date_and_time
            encounter_sim_center_node.is_deidentified = instance.is_deidentified
            encounter_sim_center_node.is_restricted = instance.is_restricted
            encounter_sim_center_node.save()

    if department is not None:
        for encounter_sim_center_node in encounter_sim_center_nodes:
            encounter_sim_center_node.department.disconnect_all()
            encounter_sim_center_node.department.connect(department)
    if encounter_source is not None:
        for encounter_sim_center_node in encounter_sim_center_nodes:
            encounter_sim_center_node.encounter_source.disconnect_all()
            encounter_sim_center_node.encounter_source.connect(
                encounter_source)
    if patient is not None:
        for encounter_sim_center_node in encounter_sim_center_nodes:
            encounter_sim_center_node.patient.disconnect_all()
            encounter_sim_center_node.patient.connect(patient)
    if provider is not None:
        for encounter_sim_center_node in encounter_sim_center_nodes:
            encounter_sim_center_node.provider.disconnect_all()
            encounter_sim_center_node.provider.connect(provider)


@receiver(post_delete, sender=EncounterSimCenter)
def delete_encounter_sim_center(sender, instance, **kwargs):
    try:
        encounter_sim_center = EncounterSimCenterNode.nodes.get(
            django_id=instance.id)
        encounter_sim_center.delete()
    except EncounterSimCenterNode.DoesNotExist:
        pass


@receiver(post_save, sender=EncounterRIAS)
def create_or_update_encounter_rias_node(sender, instance, created, **kwargs):
    department = DepartmentNode.nodes.get_or_none(
        django_id=instance.department.id) if instance.department else None
    encounter_source = EncounterSourceNode.nodes.get_or_none(
        django_id=instance.encounter_source.id) if instance.encounter_source else None
    patient = PatientNode.nodes.get_or_none(
        django_id=instance.patient.id) if instance.patient else None
    provider = ProviderNode.nodes.get_or_none(
        django_id=instance.provider.id) if instance.provider else None

    encounter_rias_nodes = EncounterRIASNode.nodes.filter(
        django_id=instance.id)

    if created:
        if not encounter_rias_nodes:
            EncounterRIASNode(
                django_id=instance.id,
                encounter_id_display=f'ENR_{instance.id}',
                case_id=instance.case_id,
                is_deidentified=instance.is_deidentified,
                is_restricted=instance.is_restricted
            ).save()
    else:
        for encounter_rias_node in encounter_rias_nodes:
            encounter_rias_node.encounter_id_display = f'ENR_{instance.id}'
            encounter_rias_node.case_id = instance.case_id
            encounter_rias_node.is_deidentified = instance.is_deidentified
            encounter_rias_node.is_restricted = instance.is_restricted
            encounter_rias_node.save()

    if department is not None:
        for encounter_rias_node in encounter_rias_nodes:
            encounter_rias_node.department.disconnect_all()
            encounter_rias_node.department.connect(department)
    if encounter_source is not None:
        for encounter_rias_node in encounter_rias_nodes:
            encounter_rias_node.encounter_source.disconnect_all()
            encounter_rias_node.encounter_source.connect(encounter_source)
    if patient is not None:
        for encounter_rias_node in encounter_rias_nodes:
            encounter_rias_node.patient.disconnect_all()
            encounter_rias_node.patient.connect(patient)
    if provider is not None:
        for encounter_rias_node in encounter_rias_nodes:
            encounter_rias_node.provider.disconnect_all()
            encounter_rias_node.provider.connect(provider)


@receiver(post_delete, sender=EncounterRIAS)
def delete_encounter_rias(sender, instance, **kwargs):
    try:
        encounter_rias = EncounterRIASNode.nodes.get(django_id=instance.id)
        encounter_rias.delete()
    except EncounterRIASNode.DoesNotExist:
        pass
