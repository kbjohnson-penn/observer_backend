from django.db import models
from shared.validators import (
    validate_field,
    validate_address,
    validate_numeric,
    validate_phone_number,
    validate_website,
)
from shared.location_choices import COUNTRY_CHOICES, GENERIC_STATE_CHOICES


class Organization(models.Model):
    name = models.CharField(max_length=100, unique=True, validators=[validate_field])
    address_1 = models.CharField(max_length=100, blank=True, null=True, validators=[validate_address])
    address_2 = models.CharField(max_length=100, blank=True, null=True, validators=[validate_address])
    city = models.CharField(max_length=100, blank=True,
                            null=True, validators=[validate_field])
    state = models.CharField(
        max_length=100, blank=True, null=True, 
        choices=GENERIC_STATE_CHOICES, validators=[validate_field],
        help_text="State/Province (use 2-letter code for US states)")
    country = models.CharField(
        max_length=100, blank=True, null=True, 
        choices=COUNTRY_CHOICES, validators=[validate_field],
        help_text="Country (2-letter ISO code preferred)")
    zip_code = models.CharField(
        max_length=5, blank=True, null=True, validators=[validate_numeric])
    phone_number = models.CharField(
        max_length=12, blank=True, null=True, validators=[validate_phone_number])
    website = models.URLField(blank=True, null=True, validators=[validate_website])

    def __str__(self):
        return self.name
    
    class Meta:
        app_label = 'accounts'