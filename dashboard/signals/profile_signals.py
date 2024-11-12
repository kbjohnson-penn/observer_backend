from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from ..models.profile_models import Profile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Check if the profile already exists
        if not Profile.objects.filter(user=instance).exists():
            Profile.objects.create(user=instance)
    else:
        instance.profile.save()