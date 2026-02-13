from django.db import models

from clinical.managers import EncounterFileManager
from shared.choices import FILE_TYPE_CHOICES, FILE_TYPE_CHOICES_DICT

from .encounter_models import Encounter


class EncounterFile(models.Model):
    encounter = models.ForeignKey(
        Encounter, related_name="files", on_delete=models.CASCADE, null=True, blank=True
    )
    file_type = models.CharField(max_length=50, choices=FILE_TYPE_CHOICES, blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.file_name:
            return f'{self.file_name} ({FILE_TYPE_CHOICES_DICT.get(self.file_type, "Unknown")})'
        elif self.file_path:
            return f"File: {self.file_path}"
        else:
            return f'{FILE_TYPE_CHOICES_DICT.get(self.file_type, "Unknown")} File #{self.id}'

    objects = EncounterFileManager()

    class Meta:
        app_label = "clinical"
        constraints = [
            models.UniqueConstraint(
                fields=["encounter", "file_path"], name="unique_file_per_encounter"
            )
        ]
