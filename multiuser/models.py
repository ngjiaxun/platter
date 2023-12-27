from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

class Organisation(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()
    users = models.ManyToManyField(User, through='OrganisationAssignment')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("organisation_detail", kwargs={"pk": self.pk})
    

class OrganisationAssignment(models.Model):
    ROLE_ADMIN = 'admin'
    ROLE_USER = 'user'
    ROLE_CHOICES = (
        (ROLE_ADMIN, 'Admin'),
        (ROLE_USER, 'User'),
    )
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.organisation.name} - {self.user.username}"


class Business(models.Model):
    name = models.CharField(max_length=100)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    industry = models.CharField(max_length=100)
    established_date = models.DateField()

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("business_detail", kwargs={"pk": self.pk})


class BusinessAssignment(models.Model):
    ROLE_ADMIN = 'admin'
    ROLE_USER = 'user'
    ROLE_CHOICES = (
        (ROLE_ADMIN, 'Admin'),
        (ROLE_USER, 'User'),
    )
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.business.name} - {self.user.username}"


class Branch(models.Model):
    name = models.CharField(max_length=100)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.name


class BranchAssignment(models.Model):
    ROLE_ADMIN = 'admin'
    ROLE_USER = 'user'
    ROLE_CHOICES = (
        (ROLE_ADMIN, 'Admin'),
        (ROLE_USER, 'User'),
    )
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.branch.name} - {self.user.username}"