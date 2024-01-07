from django.db import models
from django.db.models import Q
from django.apps import apps
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User, Group
from model_utils.managers import InheritanceManager
from guardian.shortcuts import get_objects_for_user, assign_perm
from functools import reduce


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
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.SET_DEFAULT, editable=False, default=1) 
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    objects = InheritanceManager()

    @classmethod
    def get_rank(cls):
        return settings.ENTITY_HIERARCHY.index(cls.__name__)

    @classmethod
    def is_top(cls):
        return cls.get_rank() == 0

    @classmethod
    def is_bottom(cls):
        return cls.get_rank() == len(settings.ENTITY_HIERARCHY) - 1

    @classmethod
    def get_all_models(cls):
        return [apps.get_model('multiuser', model) for model in settings.ENTITY_HIERARCHY]

    @classmethod
    def get_parent_model(cls): # Returns the model one level up in the hierarchy
        if cls.is_top():
            return None
        return apps.get_model('multiuser', settings.ENTITY_HIERARCHY[cls.get_rank() - 1])

    @classmethod
    def get_child_model(cls):
        if cls.is_bottom():
            return None
        return apps.get_model('multiuser', settings.ENTITY_HIERARCHY[cls.get_rank() + 1])

    # Returns a queryset of objects for which the user has the specified permission for the current model and ancestor models
    # E.g. queryset.filter(Q(parent__parent__in=grandparent_objects) | Q(parent__in=parent_objects) | Q(pk__in=objects))
    @classmethod
    def get_objects_for_user(cls, user, perm):
        model = cls
        queryset = model.objects.all() # Get all objects of the current model
        q_objects = [] # Filter for the queryset

        # Filter the list of objects for which the user has the specified permission for the current model
        model_str = model.__name__.lower()
        curr = get_objects_for_user(user, f'multiuser.{perm}_{model_str}')
        q_objects.append(Q(pk__in=curr))

        # Filter the list of objects for which the user has the specified permission for ancestor models
        q_key = 'in'
        while not model.is_top(): 
            model = model.get_parent_model() 
            model_str = model.__name__.lower()
            objects = get_objects_for_user(user, f'multiuser.{perm}_{model_str}')
            q_key = 'parent__' + q_key
            q_dict = {q_key: objects}
            q_objects.append(Q(**q_dict))

        conditions = reduce(lambda x, y: x | y, q_objects)
        return queryset.filter(conditions) 

    # If you have a foreign key that references the Entity base class, use this method to downcast it when you need to access subclass fields
    def select_subclass(self):
        return Entity.objects.select_subclasses().get(id=self.id)

    def get_group_name(self, role):
        return f'{self.name}_{self.pk}_{self._meta.model_name}_{settings.ENTITY_ROLES[role]["group_name"]}'

    def get_group(self, role):
        group_name = self.get_group_name(role)
        return Group.objects.filter(name=group_name).first()

    def create_groups(self):
        for role in settings.ENTITY_ROLES:
            group_name = self.get_group_name(role)
            group, created = Group.objects.get_or_create(name=group_name)
            for permission in settings.ENTITY_ROLES[role]['permissions']:
                assign_perm(f'{permission}_{self._meta.model_name}', group, self)

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
        if self.is_top() and self.parent is not None:
            raise ValidationError('Top level entities cannot have parents')
        if not self.is_top() and self.parent is None:
            raise ValidationError('Non top level entities must have parents')
        if not self.is_top() and self.get_parent_model() != self.parent.__class__:
            raise ValidationError('Parent must be of the correct type')

    def __str__(self):
        return self.name


class Organisation(Entity):
    organisation_fields = models.CharField(max_length=100)

    def get_absolute_url(self):
        return reverse("organisation_detail", kwargs={"pk": self.pk})


class Business(Entity):
    business_fields = models.CharField(max_length=100)

    def get_absolute_url(self):
        return reverse("business_detail", kwargs={"pk": self.pk})


class Branch(Entity):
    branch_fields = models.CharField(max_length=100)

    def get_absolute_url(self):
        return reverse("branch_detail", kwargs={"pk": self.pk})