from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from datetime import date
from ..models import Provider


def calculate_year_of_birth_for_max_age(born):
    today = date.today()
    age = today.year - born.year - \
        ((today.month, today.day) < (born.month, born.day))
    if age > 89:
        return today.year - 89
    return born.year
