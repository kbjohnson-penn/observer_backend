from django.db import models
from .validators import validate_name


class EncounterSource(models.Model):
    name = models.CharField(max_length=50, unique=True, validators=[validate_name])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Source'
        verbose_name_plural = 'Source'


class Department(models.Model):
    name = models.CharField(max_length=50, unique=True, validators=[validate_name])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
