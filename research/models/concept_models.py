from django.db import models


class Concept(models.Model):
    """
    This table contains records, or Concepts, that uniquely identify each fundamental unit 
    of meaning used to express clinical information. Concepts are derived from vocabularies, 
    which represent clinical information across a domain (e.g. conditions, drugs, procedures) 
    through the use of codes and associated descriptions.
    """
    concept_id = models.IntegerField(primary_key=True)
    concept_name = models.TextField()
    domain_name = models.TextField()
    vocabulary_name = models.CharField(max_length=255)  # Used in unique constraint
    concept_class_name = models.TextField()
    standard_concept = models.TextField(null=True, blank=True)
    concept_code = models.CharField(max_length=255)  # Used in unique constraint

    class Meta:
        app_label = 'research'
        db_table = 'concept'
        constraints = [
            models.UniqueConstraint(
                fields=['concept_code', 'vocabulary_name'],
                name='unique_concept_code_per_vocabulary'
            )
        ]