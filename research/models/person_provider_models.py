from django.db import models


class Person(models.Model):
    """
    This table contains demographic information about individual patients.
    """
    year_of_birth = models.IntegerField()
    gender_source_value = models.TextField()
    gender_source_concept_id = models.IntegerField()
    race_source_value = models.TextField()
    race_source_concept_id = models.IntegerField()
    ethnicity_source_value = models.TextField()
    ethnicity_source_concept_id = models.IntegerField()

    class Meta:
        app_label = 'research'
        db_table = 'person'

class Provider(models.Model):
    """
    This table stores information about healthcare providers.
    """
    year_of_birth = models.IntegerField()
    gender_source_value = models.TextField()
    gender_source_concept_id = models.IntegerField()
    race_source_value = models.TextField()
    race_source_concept_id = models.IntegerField()
    ethnicity_source_value = models.TextField()
    ethnicity_source_concept_id = models.IntegerField()

    class Meta:
        app_label = 'research'
        db_table = 'provider'