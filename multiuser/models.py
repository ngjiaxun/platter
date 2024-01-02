from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User


class Entity(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.SET_DEFAULT, editable=False, default=1) # Used to assign the user who created the instance to the admin group
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    @classmethod
    def get_rank(cls):
        return settings.ENTITY_HIERARCHY.index(cls.__name__.lower())

    @classmethod
    def is_top(cls):
        return cls.get_rank() == 0

    @classmethod
    def is_bottom(cls):
        return cls.get_rank() == len(settings.ENTITY_HIERARCHY) - 1

    @classmethod
    def prev_level(cls):
        if cls.is_top():
            return None
        return settings.ENTITY_HIERARCHY[cls.get_rank() - 1]

    @classmethod
    def curr_level(cls):
        return cls.__name__.lower()

    @classmethod
    def next_level(cls):
        if cls.is_bottom():
            return None
        return settings.ENTITY_HIERARCHY[cls.get_rank() + 1]

    def clean(self):
        # if root level entity, parent must be None
        # if leaf level entity, parent must not be None
        # if leaf level entity, parent object must be an immediate parent model in the hierarchy
        pass

    def __str__(self):
        return self.name


class Organisation(Entity):
    organisation_fields = models.CharField(max_length=100)

    def get_absolute_url(self):
        return reverse("organisation_detail", kwargs={"pk": self.pk})

    def clean(self):
        if self.parent is not None:
            raise ValidationError('Organisations cannot have parents')


class Business(Entity):
    business_fields = models.CharField(max_length=100)

    def get_absolute_url(self):
        return reverse("business_detail", kwargs={"pk": self.pk})

    # Business must have a parent and it must be an Organisation
    def clean(self):
        if self.parent is None:
            raise ValidationError('Businesses must have parents')
        if self.parent.__class__ != Organisation:
            raise ValidationError('Businesses can only have Organisations as parents')


class Branch(Entity):
    branch_fields = models.CharField(max_length=100)

    def get_absolute_url(self):
        return reverse("branch_detail", kwargs={"pk": self.pk})

    # Branch must have a parent and it must be a Business
    def clean(self):
        if self.parent is None:
            raise ValidationError('Branches must have parents')
        if self.parent.__class__ != Business:
            raise ValidationError('Branches can only have Businesses as parents')


