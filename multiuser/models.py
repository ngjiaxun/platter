from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Entity(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.SET_DEFAULT, editable=False, default=1)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Organisation(Entity):
    address = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()

    def get_absolute_url(self):
        return reverse("organisation_detail", kwargs={"pk": self.pk})


class Business(Entity):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    industry = models.CharField(max_length=100)
    established_date = models.DateField()

    def get_absolute_url(self):
        return reverse("business_detail", kwargs={"pk": self.pk})


class Branch(Entity):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()

    def get_absolute_url(self):
        return reverse("branch_detail", kwargs={"pk": self.pk})