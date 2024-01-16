from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.conf import settings
from guardian.shortcuts import assign_perm
from .models import Entity

@receiver(post_delete, sender=Entity)
def delete_entity_groups(sender, instance, **kwargs):
    instance.delete_groups()