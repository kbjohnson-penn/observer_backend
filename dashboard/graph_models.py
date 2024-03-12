from neomodel import StructuredNode, StringProperty, DateProperty, UniqueIdProperty, RelationshipTo, config
from django.conf import settings

# Configure the connection to your Neo4j database
config.DATABASE_URL = settings.NEO4J_BOLT_URL

# Example graph model definitions


class AnonymizedPatient(StructuredNode):
    uid = UniqueIdProperty()
    anonymized_id = StringProperty(unique_index=True)


class AnonymizedProvider(StructuredNode):
    uid = UniqueIdProperty()
    anonymized_id = StringProperty(unique_index=True)


class AnonymizedEncounter(StructuredNode):
    uid = UniqueIdProperty()
    encounter_date = DateProperty()
    patient = RelationshipTo(AnonymizedPatient, "HAS_PATIENT")
    provider = RelationshipTo(AnonymizedProvider, "HAS_PROVIDER")
