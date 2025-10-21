from django.db import models


class Person(models.Model):
    """
    Stores demographic information for individual patients in research database.

    Contains de-identified patient demographics including year of birth, gender,
    race, and ethnicity. Uses concept IDs for standardized medical terminology.

    Access Control:
        Access to Person records is controlled through their associated VisitOccurrences.
        Users can only access Person data if they have appropriate tier access to at least
        one visit associated with that person.

    Relationships:
        - VisitOccurrence: One person can have many visits (reverse: person.visitoccurrence_set)
        - Labs: One person can have many lab results (reverse: person.labs_set)

    Database:
        Routed to 'research' database via DatabaseRouter.
        Table: person
    """
    id = models.AutoField(primary_key=True, verbose_name="Person ID")
    year_of_birth = models.IntegerField(null=True)
    gender_source_value = models.CharField(blank=True, null=True, max_length=255)
    gender_source_concept_id = models.IntegerField(blank=True, null=True)
    race_source_value = models.CharField(blank=True, null=True, max_length=255)
    race_source_concept_id = models.IntegerField(blank=True, null=True)
    ethnicity_source_value = models.CharField(null=True, max_length=255)
    ethnicity_source_concept_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"Person {self.id}"
    class Meta:
        app_label = 'research'
        db_table = 'person'

class Provider(models.Model):
    """
    Stores demographic information for healthcare providers in research database.

    Contains de-identified provider demographics including year of birth, gender,
    race, and ethnicity. Uses concept IDs for standardized medical terminology.

    Access Control:
        Access to Provider records is controlled through their associated VisitOccurrences.
        Users can only access Provider data if they have appropriate tier access to at least
        one visit associated with that provider.

    Relationships:
        - VisitOccurrence: One provider can have many visits (reverse: provider.visitoccurrence_set)

    Database:
        Routed to 'research' database via DatabaseRouter.
        Table: provider
    """
    id = models.AutoField(primary_key=True, verbose_name="Provider ID")
    year_of_birth = models.IntegerField(null=True)
    gender_source_value = models.CharField(blank=True, null=True, max_length=255)
    gender_source_concept_id = models.IntegerField(blank=True, null=True)
    race_source_value = models.CharField(blank=True, null=True, max_length=255)
    race_source_concept_id = models.IntegerField(blank=True, null=True)
    ethnicity_source_value = models.CharField(null=True, max_length=255)
    ethnicity_source_concept_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"Provider {self.id}"
    class Meta:
        app_label = 'research'
        db_table = 'provider'