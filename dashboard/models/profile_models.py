from django.db import models
from django.contrib.auth.models import User
from .validators import validate_zip_code, validate_phone_number


class Tier(models.Model):
    tier_name = models.CharField(max_length=10)
    level = models.PositiveIntegerField(unique=True)
    complete_deidentification = models.BooleanField(default=False)
    blur_sexually_explicit_body_parts = models.BooleanField(default=False)
    blur_face = models.BooleanField(default=False)
    obscure_voice = models.BooleanField(default=False)
    dua = models.BooleanField(default=False)
    external_access = models.BooleanField(default=False)

    def __str__(self):
        return self.tier_name


class Organization(models.Model):
    name = models.CharField(max_length=100)
    address_1 = models.CharField(max_length=100, blank=True, null=True)
    address_2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=5, blank=True, null=True, validators=[validate_zip_code])
    phone_number = models.CharField(max_length=12, blank=True, null=True, validators=[validate_phone_number])
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=12, blank=True, null=True, validators=[validate_phone_number])
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    tier = models.ForeignKey(
        Tier, on_delete=models.CASCADE, null=True, blank=True)
    address_1 = models.CharField(max_length=100, blank=True, null=True)
    address_2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=5, blank=True, null=True, validators=[validate_zip_code])
    bio = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.username
