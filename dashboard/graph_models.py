from neomodel import StructuredNode, StringProperty, DateProperty, IntegerProperty, BooleanProperty, RelationshipTo, RelationshipFrom, config
from django.conf import settings

# Configure the connection to your Neo4j database
config.DATABASE_URL = settings.NEO4J_BOLT_URL


class PatientNode(StructuredNode):
    django_id = IntegerProperty(unique_index=True)
    patient_id = StringProperty(unique_index=True)
    patient_id_display = StringProperty(unique_index=True)
    year_of_birth = IntegerProperty()
    sex = StringProperty()
    race = StringProperty()
    ethnicity = StringProperty()
    encounters = RelationshipFrom('EncounterNode', 'HAS_PATIENT')


class ProviderNode(StructuredNode):
    django_id = IntegerProperty(unique_index=True)
    provider_id = StringProperty(unique_index=True)
    provider_id_display = StringProperty(unique_index=True)
    year_of_birth = IntegerProperty()
    sex = StringProperty()
    race = StringProperty()
    ethnicity = StringProperty()
    encounters = RelationshipFrom('EncounterNode', 'HAS_PROVIDER')


class EncounterSourceNode(StructuredNode):
    django_id = IntegerProperty(unique_index=True)
    name = StringProperty(unique_index=True)
    encounters = RelationshipFrom('EncounterNode', 'HAS_SOURCE')


class DepartmentNode(StructuredNode):
    django_id = IntegerProperty(unique_index=True)
    name = StringProperty(unique_index=True)
    encounters = RelationshipFrom('EncounterNode', 'OCCURRED_IN_DEPARTMENT')


class EncounterNode(StructuredNode):
    django_id = IntegerProperty(unique_index=True)
    encouter_id = StringProperty(unique_index=True)
    encouter_id_display = StringProperty()
    encounter_date_and_time = DateProperty()
    patient_satisfaction = IntegerProperty()
    provider_satisfaction = IntegerProperty()
    is_deidentified = BooleanProperty()
    is_restricted = BooleanProperty()

    patient = RelationshipTo('PatientNode', 'HAS_PATIENT')
    provider = RelationshipTo('ProviderNode', 'HAS_PROVIDER')
    encounter_source = RelationshipTo('EncounterSourceNode', 'HAS_SOURCE')
    department = RelationshipTo('DepartmentNode', 'OCCURRED_IN_DEPARTMENT')
    

class EncounterSimCenterNode(StructuredNode):
    django_id = IntegerProperty(unique_index=True)
    encounter_id = StringProperty(unique_index=True)
    encounter_id_display = StringProperty()
    case_id = StringProperty(unique_index=True)
    encounter_date_and_time = DateProperty()
    is_deidentified = BooleanProperty()
    is_restricted = BooleanProperty()

    patient = RelationshipTo('PatientNode', 'HAS_PATIENT')
    provider = RelationshipTo('ProviderNode', 'HAS_PROVIDER')
    encounter_source = RelationshipTo('EncounterSourceNode', 'HAS_SOURCE')
    department = RelationshipTo('DepartmentNode', 'OCCURRED_IN_DEPARTMENT')
    

class EncounterRIASNode(StructuredNode):
    django_id = IntegerProperty(unique_index=True)
    encounter_id = StringProperty(unique_index=True)
    encounter_id_display = StringProperty()
    case_id = StringProperty(unique_index=True)
    encounter_date_and_time = DateProperty()
    is_deidentified = BooleanProperty()
    is_restricted = BooleanProperty()

    patient = RelationshipTo('PatientNode', 'HAS_PATIENT')
    provider = RelationshipTo('ProviderNode', 'HAS_PROVIDER')
    encounter_source = RelationshipTo('EncounterSourceNode', 'HAS_SOURCE')
    department = RelationshipTo('DepartmentNode', 'OCCURRED_IN_DEPARTMENT')
    