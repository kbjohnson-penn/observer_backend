from django.db import models
from dashboard.choices import SEX_CATEGORIES, RACIAL_CATEGORIES, ETHNIC_CATEGORIES
from .validators import validate_name, validate_time


class Provider(models.Model):
    provider_id = models.PositiveIntegerField(unique=True)
    first_name = models.CharField(max_length=255, blank=True, validators=[validate_name])
    last_name = models.CharField(max_length=255, blank=True, validators=[validate_name])
    date_of_birth = models.DateField(blank=True, null=True, validators=[validate_time])
    sex = models.CharField(max_length=5, choices=SEX_CATEGORIES, blank=True)
    race = models.CharField(
        max_length=5, choices=RACIAL_CATEGORIES, blank=True)
    ethnicity = models.CharField(
        max_length=5, choices=ETHNIC_CATEGORIES, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'PR{self.provider_id}'

    class Meta:
        verbose_name = 'Provider'
        verbose_name_plural = 'Providers'
