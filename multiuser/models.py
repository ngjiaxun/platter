from django.db import models
from django.urls import reverse


class Organisation(models.Model):
    name = models.CharField(max_length=100)
    organisation_fields = models.CharField(max_length=100)

    def get_absolute_url(self):
        return reverse("organisation_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name


class Business(models.Model):
    name = models.CharField(max_length=100)
    business_fields = models.CharField(max_length=100)

    def get_absolute_url(self):
        return reverse("business_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name


class Branch(models.Model):
    name = models.CharField(max_length=100)
    branch_fields = models.CharField(max_length=100)

    def get_absolute_url(self):
        return reverse("branch_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name