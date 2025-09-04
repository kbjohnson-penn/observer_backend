from django.db import models


class Concept(models.Model):
    """
    This table contains records, or Concepts, that uniquely identify each fundamental unit 
    of meaning used to express clinical information. Concepts are derived from vocabularies, 
    which represent clinical information across a domain (e.g. conditions, drugs, procedures) 
    through the use of codes and associated descriptions.
    """
    concept_id = models.IntegerField(primary_key=True)
    concept_name = models.CharField(max_length=255)
    domain_name = models.CharField(max_length=255)
    vocabulary_name = models.CharField(max_length=255)
    concept_class_name = models.CharField(max_length=255)
    standard_concept = models.CharField(max_length=255, null=True, blank=True)
    concept_code = models.CharField(max_length=255)

    def __str__(self):
        return f"Concept ID ({self.id})"
    class Meta:
        app_label = 'research'
        db_table = 'concept'
        constraints = [
            models.UniqueConstraint(
                fields=['concept_code', 'vocabulary_name'],
                name='unique_concept_code_per_vocabulary'
            )
        ]