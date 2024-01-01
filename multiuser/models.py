from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Entity(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.SET_DEFAULT, editable=False, default=1)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

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