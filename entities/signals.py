from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Entity

@receiver(post_delete, sender=Entity)
def delete_entity_groups(sender, instance, **kwargs):
    instance.delete_groups()