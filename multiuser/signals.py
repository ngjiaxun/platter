from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission, User
from guardian.shortcuts import assign_perm
from .models import Organisation, Business, Branch

def create_groups(instance, created):
    if created:
        # Create the admin group
        admin_group, created = Group.objects.get_or_create(name=f'{instance.name}{instance.pk}_{instance._meta.model_name}_admins')
        # Assign all permissions for the instance to the admin group
        assign_perm(f'view_{instance._meta.model_name}', admin_group, instance)
        assign_perm(f'change_{instance._meta.model_name}', admin_group, instance)
        assign_perm(f'delete_{instance._meta.model_name}', admin_group, instance)

        # Create the user group
        user_group, created = Group.objects.get_or_create(name=f'{instance.name}{instance.pk}_{instance._meta.model_name}_users')
        # Assign the view permission for the instance to the user group
        assign_perm(f'view_{instance._meta.model_name}', user_group, instance)

        # Add the user who created the instance to the admin group
        instance.created_by.groups.add(admin_group)

def delete_groups(instance):
    Group.objects.get(name=f'{instance.name}_{instance._meta.model_name}_admins').delete()
    Group.objects.get(name=f'{instance.name}_{instance._meta.model_name}_users').delete()

@receiver(post_save, sender=Organisation)
def create_organisation_groups(sender, instance, created, **kwargs):
    create_groups(instance, created)

@receiver(post_delete, sender=Organisation)
def delete_organisation_groups(sender, instance, **kwargs):
    delete_groups(instance)

@receiver(post_save, sender=Business)
def create_business_groups(sender, instance, created, **kwargs):
    create_groups(instance, created)

@receiver(post_delete, sender=Business)
def delete_business_groups(sender, instance, **kwargs):
    delete_groups(instance)

@receiver(post_save, sender=Branch)
def create_branch_groups(sender, instance, created, **kwargs):
    create_groups(instance, created)

@receiver(post_delete, sender=Branch)
def delete_branch_groups(sender, instance, **kwargs):
    delete_groups(instance)