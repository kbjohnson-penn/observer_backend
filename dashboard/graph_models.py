from neomodel import StructuredNode, StringProperty, DateProperty, UniqueIdProperty, RelationshipTo, config
from django.conf import settings

# Configure the connection to your Neo4j database
config.DATABASE_URL = settings.NEO4J_BOLT_URL


class GraphPatient(StructuredNode):
    patient_id = StringProperty(unique_index=True)
    date_of_birth = DateProperty()
    sex = StringProperty()
    race = StringProperty()
    ethnicity = StringProperty()


class GraphProvider(StructuredNode):
    provider_id = StringProperty(unique_index=True)
    date_of_birth = DateProperty()
    sex = StringProperty()
    race = StringProperty()
    ethnicity = StringProperty()


class GraphDepartment(StructuredNode):
    name = StringProperty(unique_index=True)


class GraphEncounter(StructuredNode):
    case_id = StringProperty(unique_index=True)
    encounter_date = DateProperty()
    patient = RelationshipTo('GraphPatient', 'VISITED_BY')
    provider = RelationshipTo('GraphProvider', 'ATTENDED_BY')
    department = RelationshipTo('GraphDepartment', 'BELONGS_TO')
