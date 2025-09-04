from django.db import models


class Person(models.Model):
    """
    This table contains demographic information about individual patients.
    """
    year_of_birth = models.IntegerField(null=True)
    gender_source_value = models.CharField(blank=True, null=True, max_length=255)
    gender_source_concept_id = models.IntegerField(blank=True, null=True)
    race_source_value = models.CharField(blank=True, null=True, max_length=255)
    race_source_concept_id = models.IntegerField(blank=True, null=True)
    ethnicity_source_value = models.CharField(null=True, max_length=255)
    ethnicity_source_concept_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"Person ID ({self.id})"
    class Meta:
        app_label = 'research'
        db_table = 'person'

class Provider(models.Model):
    """
    This table stores information about healthcare providers.
    """
    year_of_birth = models.IntegerField(null=True)
    gender_source_value = models.CharField(blank=True, null=True, max_length=255)
    gender_source_concept_id = models.IntegerField(blank=True, null=True)
    race_source_value = models.CharField(blank=True, null=True, max_length=255)
    race_source_concept_id = models.IntegerField(blank=True, null=True)
    ethnicity_source_value = models.CharField(null=True, max_length=255)
    ethnicity_source_concept_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"Provider ID ({self.id})"
    class Meta:
        app_label = 'research'
        db_table = 'provider'