from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission, User
from django.conf import settings
from guardian.shortcuts import assign_perm
from .models import Organisation, Business, Branch

def _create_groups(instance, created):
    if created:
        admin_role = settings.ENTITY_ROLES[0].lower() + 's'
        user_role = settings.ENTITY_ROLES[1].lower() + 's'

        # Create the admin group
        admin_group, created = Group.objects.get_or_create(name=f'{instance.name}_{instance.pk}_{instance._meta.model_name}_{admin_role}')
        # Assign all permissions for the instance to the admin group
        assign_perm(f'view_{instance._meta.model_name}', admin_group, instance)
        assign_perm(f'change_{instance._meta.model_name}', admin_group, instance)
        assign_perm(f'delete_{instance._meta.model_name}', admin_group, instance)

        # Create the user group
        user_group, created = Group.objects.get_or_create(name=f'{instance.name}_{instance.pk}_{instance._meta.model_name}_{user_role}')
        # Assign the view permission for the instance to the user group
        assign_perm(f'view_{instance._meta.model_name}', user_group, instance)

        # Add the user who created the instance to the admin group
        instance.created_by.groups.add(admin_group)

def _delete_groups(instance):
    admins_group = Group.objects.filter(name=f'{instance.name}_{instance._meta.model_name}_admins').first()
    users_group = Group.objects.filter(name=f'{instance.name}_{instance._meta.model_name}_users').first()
    if admins_group is not None:
        admins_group.delete()
    if users_group is not None:
        users_group.delete()

# Whenever an entity object is created, create the admin and user groups for that entity
@receiver(post_save, sender=Organisation)
def create_organisation_groups(sender, instance, created, **kwargs):
    _create_groups(instance, created)

# Whenever an entity object is deleted, delete the admin and user groups for that entity
@receiver(post_delete, sender=Organisation)
def delete_organisation_groups(sender, instance, **kwargs):
    _delete_groups(instance)

@receiver(post_save, sender=Business)
def create_business_groups(sender, instance, created, **kwargs):
    _create_groups(instance, created)

@receiver(post_delete, sender=Business)
def delete_business_groups(sender, instance, **kwargs):
    _delete_groups(instance)

@receiver(post_save, sender=Branch)
def create_branch_groups(sender, instance, created, **kwargs):
    _create_groups(instance, created)

@receiver(post_delete, sender=Branch)
def delete_branch_groups(sender, instance, **kwargs):
    _delete_groups(instance)