from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from ..models.provider_models import Provider
from ..graph_models import ProviderNode
from datetime import date

def calculate_year_of_birth_for_max_age(born):
    today = date.today()
    age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    if age > 89:
        return today.year - 89
    return born.year

@receiver(post_save, sender=Provider)
def create_or_update_provider(sender, instance, created, **kwargs):
    if created:
        ProviderNode(
            provider_id=instance.provider_id,
            provider_id_display=f'PR{instance.provider_id}',
            year_of_birth=calculate_year_of_birth_for_max_age(instance.date_of_birth) if instance.date_of_birth else None,
            sex=instance.sex,
            race=instance.race,
            ethnicity=instance.ethnicity,
            django_id=instance.id
        ).save()
    else:
        provider_node = ProviderNode.nodes.get(django_id=instance.id)
        provider_node.provider_id = instance.provider_id
        provider_node.provider_id_display = f'PR{instance.provider_id}'
        provider_node.year_of_birth = calculate_year_of_birth_for_max_age(instance.date_of_birth) if instance.date_of_birth else None
        provider_node.sex = instance.sex
        provider_node.race = instance.race
        provider_node.ethnicity = instance.ethnicity
        provider_node.save()

@receiver(post_delete, sender=Provider)
def delete_provider(sender, instance, **kwargs):
    try:
        provider_node = ProviderNode.nodes.get(django_id=instance.id)
        provider_node.delete()
    except ProviderNode.DoesNotExist:
        pass