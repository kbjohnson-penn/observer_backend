from neomodel import StructuredNode, StringProperty, DateProperty, IntegerProperty, BooleanProperty, RelationshipTo, RelationshipFrom, config
from django.conf import settings

# Configure the connection to your Neo4j database
config.DATABASE_URL = settings.NEO4J_BOLT_URL


class PatientNode(StructuredNode):
    patient_id = StringProperty(unique_index=True)
    date_of_birth = DateProperty()
    sex = StringProperty()
    race = StringProperty()
    ethnicity = StringProperty()
    encounters = RelationshipFrom('EncounterNode', 'HAS_PATIENT')


class ProviderNode(StructuredNode):
    provider_id = StringProperty(unique_index=True)
    date_of_birth = DateProperty()
    sex = StringProperty()
    race = StringProperty()
    ethnicity = StringProperty()
    encounters = RelationshipFrom('EncounterNode', 'HAS_PROVIDER')


class EncounterSourceNode(StructuredNode):
    name = StringProperty(unique_index=True)
    encounters = RelationshipFrom('EncounterNode', 'HAS_SOURCE')


class DepartmentNode(StructuredNode):
    name = StringProperty(unique_index=True)
    encounters = RelationshipFrom('EncounterNode', 'OCCURRED_IN_DEPARTMENT')


class MultiModalDataPathNode(StructuredNode):
    multi_modal_data_id = StringProperty(unique_index=True)
    provider_view = StringProperty()
    patient_view = StringProperty()
    room_view = StringProperty()
    audio = StringProperty()
    transcript = StringProperty()
    patient_survey = StringProperty()
    provider_survey = StringProperty()
    rias_transcript = StringProperty()
    rias_codes = StringProperty()
    encounters = RelationshipFrom(
        'EncounterNode', 'ASSOCIATED_WITH_MULTI_MODAL_DATA')


class EncounterNode(StructuredNode):
    case_id = StringProperty(unique_index=True)
    encounter_date_and_time = DateProperty()
    patient_satisfaction = IntegerProperty()
    provider_satisfaction = IntegerProperty()
    is_deidentified = BooleanProperty()
    is_restricted = BooleanProperty()

    patient = RelationshipTo('PatientNode', 'HAS_PATIENT')
    provider = RelationshipTo('ProviderNode', 'HAS_PROVIDER')
    encounter_source = RelationshipTo('EncounterSourceNode', 'HAS_SOURCE')
    department = RelationshipTo('DepartmentNode', 'OCCURRED_IN_DEPARTMENT')
    data_paths = RelationshipTo(
        'MultiModalDataPathNode', 'ASSOCIATED_WITH_MULTI_MODAL_DATA')
