from django.db import models
from django.contrib.auth.models import User
from .validators import validate_numeric, validate_phone_number, validate_name


class Tier(models.Model):
    tier_name = models.CharField(max_length=10, validators=[validate_name])
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
    name = models.CharField(max_length=100, validators=[validate_name])
    address_1 = models.CharField(max_length=100, blank=True, null=True)
    address_2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True,
                            null=True, validators=[validate_name])
    state = models.CharField(max_length=100, blank=True,
                             null=True, validators=[validate_name])
    country = models.CharField(
        max_length=100, blank=True, null=True, validators=[validate_name])
    zip_code = models.CharField(
        max_length=5, blank=True, null=True, validators=[validate_numeric])
    phone_number = models.CharField(
        max_length=12, blank=True, null=True, validators=[validate_phone_number])
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(
        max_length=12, blank=True, null=True, validators=[validate_phone_number])
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    tier = models.ForeignKey(
        Tier, on_delete=models.CASCADE, null=True, blank=True)
    address_1 = models.CharField(max_length=100, blank=True, null=True)
    address_2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True,
                            null=True, validators=[validate_name])
    state = models.CharField(max_length=100, blank=True,
                             null=True, validators=[validate_name])
    country = models.CharField(
        max_length=100, blank=True, null=True, validators=[validate_name])
    zip_code = models.CharField(
        max_length=5, blank=True, null=True, validators=[validate_numeric])
    bio = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.user.username
