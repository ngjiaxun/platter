from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
from model_utils.managers import InheritanceManager


class Entity(models.Model):
    objects = InheritanceManager()

    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.SET_DEFAULT, editable=False, default=1) # Used to assign the user who created the instance to the admin group
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

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
    def prev_level(cls): # Returns the name of the model one level up in the hierarchy as a string
        if cls.is_top():
            return None
        return settings.ENTITY_HIERARCHY[cls.get_rank() - 1]

    @classmethod
    def curr_level(cls): # Returns the name of the model as a string
        return cls.__name__

    @classmethod
    def next_level(cls): # Returns the name of the model one level down in the hierarchy as a string
        if cls.is_bottom():
            return None
        return settings.ENTITY_HIERARCHY[cls.get_rank() + 1]

    def get_parent(self): # Returns the parent instance as the correct subclass instead of just an Entity instance
        return Entity.objects.select_subclasses().get(id=self.parent.id)

    def clean(self):
        if self.is_top() and self.parent is not None:
            raise ValidationError('Top level entities cannot have parents')
        if not self.is_top() and self.parent is None:
            raise ValidationError('Non top level entities must have parents')
        if not self.is_top() and self.get_parent().curr_level() != self.prev_level():
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