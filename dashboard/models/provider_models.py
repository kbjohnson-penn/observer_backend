from django.db import models

SEX_CATEGORIES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('UN', 'Unknown or Not Reported')
]

RACIAL_CATEGORIES = [
    ('AI', 'American Indian or Alaska Native'),
    ('A', 'Asian'),
    ('NHPI', 'Native Hawaiian or Other Pacific Islander'),
    ('B', 'Black or African American'),
    ('W', 'White'),
    ('M', 'More than One Race'),
    ('UN', 'Unknown or Not Reported'),
]

ETHNIC_CATEGORIES = [
    ('H', 'Hispanic or Latino'),
    ('NH', 'Not Hispanic or Latino'),
    ('UN', 'Unknown or Not Reported Ethnicity'),
]

class Provider(models.Model):
    provider_id = models.PositiveIntegerField(unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
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