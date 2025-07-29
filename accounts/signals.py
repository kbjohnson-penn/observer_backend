from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, using, **kwargs):
    """
    Automatically create a Profile when a new User is created.
    Creates the Profile in the same database as the User.
    """
    if created:
        # Create Profile in the same database as the User
        Profile.objects.using(using).get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, using, **kwargs):
    """
    Ensure profile is saved when user is saved.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save(using=using)