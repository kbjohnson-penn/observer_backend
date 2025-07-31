from django.db import models
from django.core.validators import MaxValueValidator
from shared.validators import validate_field


class Tier(models.Model):
    tier_name = models.CharField(max_length=10, unique=True, validators=[validate_field])
    level = models.PositiveIntegerField(unique=True, validators=[MaxValueValidator(5)])
    complete_deidentification = models.BooleanField(default=False)
    blur_sexually_explicit_body_parts = models.BooleanField(default=False)
    blur_face = models.BooleanField(default=False)
    obscure_voice = models.BooleanField(default=False)
    dua = models.BooleanField(default=False)
    external_access = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.tier_name} (Level {self.level})"
    
    class Meta:
        app_label = 'accounts'
        ordering = ['level']
        verbose_name = 'Tier'
        verbose_name_plural = 'Tiers'