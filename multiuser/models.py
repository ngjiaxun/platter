from django.db import models
from django.db.models import Q
from django.apps import apps
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from guardian.shortcuts import get_objects_for_user, assign_perm
from functools import reduce
import time



class Invitation(models.Model):
    email = models.EmailField()
    entity = models.ForeignKey('Entity', on_delete=models.CASCADE) 
    role = models.CharField(max_length=100, choices=[(role, role) for role in settings.ENTITY_ROLES])
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    accepted = models.BooleanField(default=False, editable=False)

    def accept(self, user):
        entity = self.entity.select_subclass() # Downcast
        group_name = entity.get_group_name(self.role)
        group = entity.get_group(self.role)
        user.groups.add(group)
        self.accepted = True
        self.save()

    def __str__(self):
        return self.email


class Entity(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_DEFAULT, editable=False, default=1) 
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    # Content type fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, editable=False)
    object_id = models.PositiveIntegerField(editable=False)
    content_object = GenericForeignKey('content_type', 'object_id')

    @staticmethod
    def get_top_model():
        return apps.get_model('multiuser', settings.ENTITY_HIERARCHY[0])

    @staticmethod
    def get_bottom_model():
        return apps.get_model('multiuser', settings.ENTITY_HIERARCHY[-1])

    @staticmethod
    def get_all_models():
        return [apps.get_model('multiuser', model) for model in settings.ENTITY_HIERARCHY]

    @staticmethod
    def get_role(group_name): # Admin, User, etc...
        group_name = group_name.split('_')[-1]
        for role, role_data in settings.ENTITY_ROLES.items():
            if role_data['group_name'] == group_name:
                return role
        return None

    @staticmethod
    def get_rank(model):
        return settings.ENTITY_HIERARCHY.index(model.__name__)

    @staticmethod
    def is_top(model):
        return Entity.get_rank(model) == 0

    @staticmethod
    def is_bottom(model):
        return Entity.get_rank(model) == len(settings.ENTITY_HIERARCHY) - 1

    @staticmethod
    def get_parent(model): # Returns the model one level up in the hierarchy
        if Entity.is_top(model):
            return None
        return apps.get_model('multiuser', settings.ENTITY_HIERARCHY[Entity.get_rank(model) - 1])

    @staticmethod
    def get_child(model):
        if Entity.is_bottom(model):
            return None
        return apps.get_model('multiuser', settings.ENTITY_HIERARCHY[Entity.get_rank(model) + 1])

    # Returns a queryset of objects for which the user has the specified permission for the current model and ancestor models
    # E.g. queryset.filter(Q(parent__parent__in=grandparent_objects) | Q(parent__in=parent_objects) | Q(pk__in=objects))
    @staticmethod
    def get_objects_for_user(model, user, perm):
        model_type = ContentType.objects.get_for_model(model)
        entities = Entity.objects.all().filter(content_type=model_type) # Get all entity objects of which the content type is the current model
        perm_str = f'multiuser.{perm}_{Entity.__name__.lower()}'
        q_objects = [] # Filter for the queryset

        # Create a filter of the list of objects for which the user has the specified permission for the current model
        curr = get_objects_for_user(user, perm_str).filter(content_type=model_type)
        q_objects.append(Q(pk__in=curr))

        # Create filters of lists of objects for which the user has the specified permission for ancestor models
        q_key = 'in'
        while not Entity.is_top(model): 
            model = Entity.get_parent(model) 
            objects = get_objects_for_user(user, perm_str).filter(content_type=ContentType.objects.get_for_model(model))
            q_key = 'parent__' + q_key
            q_dict = {q_key: objects}
            q_objects.append(Q(**q_dict))

        # Combine the filters and filter the entities
        conditions = reduce(lambda x, y: x | y, q_objects)
        entities.filter(conditions)

        # Return a queryset of model objects corresponding to the filtered entities
        return model.objects.filter(pk__in=entities.values_list('object_id', flat=True))

    def get_group_name(self, role): # E.g. ABC Corp_42_organisation_admins
        return f'{self.content_object.name}_{self.pk}_{self.content_type.model}_{settings.ENTITY_ROLES[role]["group_name"]}'

    def get_group(self, role):
        group_name = self.get_group_name(role)
        return Group.objects.filter(name=group_name).first()

    # Create the admin group and other groups for this entity instance
    def create_groups(self): 
        for role in settings.ENTITY_ROLES:
            group_name = self.get_group_name(role)
            group, created = Group.objects.get_or_create(name=group_name)
            print(f'Group: {group}, Created: {created}')
            for permission in settings.ENTITY_ROLES[role]['permissions']:
                permission_string = f'{permission}_{Entity.__name__.lower()}'
                assign_perm(permission_string, group, self)

    def delete_groups(self):
        for role in settings.ENTITY_ROLES:
            group_name = self.get_group_name(role)
            group = Group.objects.filter(name=group_name).first()
            if group is not None:
                group.delete()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Create the admin group and other groups for this entity instance
        self.create_groups()
        # Add the user who created the entity instance to its admin group
        self.created_by.groups.add(self.get_group(settings.ENTITY_ROLE_ADMIN))

    def clean(self):
        if Entity.is_top(model) and self.parent is not None:
            raise ValidationError('Top level entities cannot have parents')
        if not Entity.is_top(model) and self.parent is None:
            raise ValidationError('Non top level entities must have parents')
        if not Entity.is_top(model) and self.get_parent() != self.parent.content_type.model_class():
            raise ValidationError('Parent must be of the correct type')

    def __str__(self):
        return self.content_object.name


class Organisation(models.Model):
    name = models.CharField(max_length=100)
    organisation_fields = models.CharField(max_length=100)

    def get_absolute_url(self):
        return reverse("organisation_detail", kwargs={"pk": self.pk})


class Business(models.Model):
    name = models.CharField(max_length=100)
    business_fields = models.CharField(max_length=100)

    def get_absolute_url(self):
        return reverse("business_detail", kwargs={"pk": self.pk})


class Branch(models.Model):
    name = models.CharField(max_length=100)
    branch_fields = models.CharField(max_length=100)

    def get_absolute_url(self):
        return reverse("branch_detail", kwargs={"pk": self.pk})