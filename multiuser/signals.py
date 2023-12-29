from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from guardian.shortcuts import assign_perm
from .models import Organisation, Business, Branch

@receiver(post_save, sender=Organisation)
def create_organisation_groups(sender, instance, created, **kwargs):
    if created:
        # Create the admin group
        admin_group, created = Group.objects.get_or_create(name=f'{instance.name}_{instance._meta.model_name}_admins')
        # Assign all permissions for the Organisation instance to the admin group
        assign_perm('view_organisation', admin_group, instance)
        assign_perm('change_organisation', admin_group, instance)
        assign_perm('delete_organisation', admin_group, instance)

        # Create the user group
        user_group, created = Group.objects.get_or_create(name=f'{instance.name}_{instance._meta.model_name}_users')
        # Assign the view permission for the Organisation instance to the user group
        assign_perm('view_organisation', user_group, instance)

        # Add the user who created the organisation to the admin group
        instance.created_by.groups.add(admin_group)

@receiver(post_delete, sender=Organisation)
def delete_organisation_groups(sender, instance, **kwargs):
    # Delete the admin group
    Group.objects.get(name=f'{instance.name}_admins').delete()
    # Delete the user group
    Group.objects.get(name=f'{instance.name}_users').delete()

@receiver(post_save, sender=Business)
def create_business_groups(sender, instance, created, **kwargs):
    if created:
        # Create the admin group
        admin_group, created = Group.objects.get_or_create(name=f'{instance.name}_{instance._meta.model_name}_admins')
        # Assign all permissions for the Business instance to the admin group
        assign_perm('view_business', admin_group, instance)
        assign_perm('change_business', admin_group, instance)
        assign_perm('delete_business', admin_group, instance)

        # Create the user group
        user_group, created = Group.objects.get_or_create(name=f'{instance.name}_{instance._meta.model_name}_users')
        # Assign the view permission for the Business instance to the user group
        assign_perm('view_business', user_group, instance)

        # Add the user who created the business to the admin group
        instance.created_by.groups.add(admin_group)

@receiver(post_delete, sender=Business)
def delete_business_groups(sender, instance, **kwargs):
    # Delete the admin group
    Group.objects.get(name=f'{instance.name}_admins').delete()
    # Delete the user group
    Group.objects.get(name=f'{instance.name}_users').delete()

@receiver(post_save, sender=Branch)
def create_branch_groups(sender, instance, created, **kwargs):
    if created:
        # Create the admin group
        admin_group, created = Group.objects.get_or_create(name=f'{instance.name}_{instance._meta.model_name}_admins')
        # Assign all permissions for the Branch instance to the admin group
        assign_perm('view_branch', admin_group, instance)
        assign_perm('change_branch', admin_group, instance)
        assign_perm('delete_branch', admin_group, instance)

        # Create the user group
        user_group, created = Group.objects.get_or_create(name=f'{instance.name}_{instance._meta.model_name}_users')
        # Assign the view permission for the Branch instance to the user group
        assign_perm('view_branch', user_group, instance)

        # Add the user who created the branch to the admin group
        instance.created_by.groups.add(admin_group)

@receiver(post_delete, sender=Branch)
def delete_branch_groups(sender, instance, **kwargs):
    # Delete the admin group
    Group.objects.get(name=f'{instance.name}_admins').delete()
    # Delete the user group
    Group.objects.get(name=f'{instance.name}_users').delete()