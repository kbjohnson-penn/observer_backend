# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Patient, Provider, Department, Encounter
# from .graph_models import GraphPatient, GraphProvider, GraphDepartment, GraphEncounter


# @receiver(post_save, sender=Patient)
# def create_patient(sender, instance, created, **kwargs):
#     if created:
#         if not GraphPatient.nodes.filter(patient_id=instance.patient_id):
#             GraphPatient(
#                 patient_id=instance.patient_id,
#                 date_of_birth=instance.date_of_birth,
#                 sex=instance.sex,
#                 race=instance.race,
#                 ethnicity=instance.ethnicity
#             ).save()


# @receiver(post_save, sender=Provider)
# def create_provider(sender, instance, created, **kwargs):
#     if created:
#         if not GraphProvider.nodes.filter(provider_id=instance.provider_id):
#             GraphProvider(
#                 provider_id=instance.provider_id,
#                 date_of_birth=instance.date_of_birth,
#                 sex=instance.sex,
#                 race=instance.race,
#                 ethnicity=instance.ethnicity
#             ).save()


# @receiver(post_save, sender=Department)
# def create_department(sender, instance, created, **kwargs):
#     if created:
#         if not GraphDepartment.nodes.filter(name=instance.name):
#             GraphDepartment(name=instance.name).save()


# @receiver(post_save, sender=Encounter)
# def create_encounter(sender, instance, created, **kwargs):
#     if created:
#         if not GraphEncounter.nodes.filter(case_id=instance.case_id):
#             encounter = GraphEncounter(
#                 case_id=instance.case_id,
#                 encounter_date=instance.encounter_date
#             ).save()
#             # Check if the patient field is set
#             if instance.patient is None:
#                 raise ValueError(
#                     "The patient field in the Encounter instance is not set")

#             if instance.provider is None:
#                 raise ValueError(
#                     "The provider field in the Encounter instance is not set")

#             # Check if the GraphPatient node exists
#             if not GraphPatient.nodes.filter(patient_id=instance.patient):
#                 raise ValueError(
#                     f"No GraphPatient node with patient_id={instance.patient}")

#             patient = GraphPatient.nodes.get(
#                 patient_id=instance.patient)
#             provider = GraphProvider.nodes.get(
#                 provider_id=instance.provider)
#             department = GraphDepartment.nodes.get(
#                 name=instance.department.name)

#             encounter.patient.connect(patient)
#             encounter.provider.connect(provider)
#             encounter.department.connect(department)
