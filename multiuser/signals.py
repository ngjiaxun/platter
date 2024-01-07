from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.conf import settings
from guardian.shortcuts import assign_perm
from .models import *

@receiver(post_delete, sender=Organisation)
def delete_organisation_groups(sender, instance, **kwargs):
    instance.delete_groups()

@receiver(post_delete, sender=Business)
def delete_business_groups(sender, instance, **kwargs):
    instance.delete_groups()

@receiver(post_delete, sender=Branch)
def delete_branch_groups(sender, instance, **kwargs):
    instance.delete_groups()
