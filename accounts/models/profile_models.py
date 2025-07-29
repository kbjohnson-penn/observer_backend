from django.db import models
from django.conf import settings
from shared.validators import (
    validate_field,
    validate_address,
    validate_numeric,
    validate_phone_number,
    validate_time,
)
from shared.location_choices import COUNTRY_CHOICES, GENERIC_STATE_CHOICES
from .organization_models import Organization
from .tier_models import Tier


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    date_of_birth = models.DateField(blank=True, null=True, validators=[validate_time])
    phone_number = models.CharField(
        max_length=12, blank=True, null=True, validators=[validate_phone_number])
    organization = models.ForeignKey(
        Organization, on_delete=models.SET_NULL, null=True, blank=True)
    tier = models.ForeignKey(
        Tier, on_delete=models.SET_NULL, null=True, blank=True)
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
    bio = models.CharField(max_length=200, blank=True, null=True, validators=[validate_field])

    def __str__(self):
        return f"Profile({self.user.username})"
    
    class Meta:
        app_label = 'accounts'