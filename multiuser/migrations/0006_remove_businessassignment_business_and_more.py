# Generated by Django 5.0 on 2023-12-28 13:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('multiuser', '0005_branchassignment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='businessassignment',
            name='business',
        ),
        migrations.RemoveField(
            model_name='businessassignment',
            name='user',
        ),
        migrations.RemoveField(
            model_name='organisationassignment',
            name='organisation',
        ),
        migrations.RemoveField(
            model_name='organisationassignment',
            name='user',
        ),
        migrations.RemoveField(
            model_name='organisation',
            name='users',
        ),
        migrations.DeleteModel(
            name='BranchAssignment',
        ),
        migrations.DeleteModel(
            name='BusinessAssignment',
        ),
        migrations.DeleteModel(
            name='OrganisationAssignment',
        ),
    ]