# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth.models import Group, Permission
# from guardian.shortcuts import assign_perm
# from .models import Organisation

# @receiver(post_save, sender=Organisation)
# def create_organisation_groups(sender, instance, created, **kwargs):
#     if created:
#         # Create the admin group
#         admin_group, created = Group.objects.get_or_create(name=f'{instance.name}_admins')
#         # Assign all permissions for the Organisation instance to the admin group
#         assign_perm('view_organisation', admin_group, instance)
#         assign_perm('change_organisation', admin_group, instance)
#         assign_perm('delete_organisation', admin_group, instance)

#         # Create the user group
#         user_group, created = Group.objects.get_or_create(name=f'{instance.name}_users')
#         # Assign the view permission for the Organisation instance to the user group
#         assign_perm('view_organisation', user_group, instance)

#         # Add the user who created the organisation to the admin group
#         instance.created_by.groups.add(admin_group)