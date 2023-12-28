from django.contrib import admin
from .models import *
from guardian.admin import GuardedModelAdmin

# admin.site.register(Organisation)
# admin.site.register(Business)
# admin.site.register(Branch)
# admin.site.register(OrganisationAssignment)
# admin.site.register(BusinessAssignment)
# admin.site.register(BranchAssignment)

@admin.register(Organisation)
class OrganisationAdmin(GuardedModelAdmin):
    list_display = ('name', )

@admin.register(Business)
class BusinessAdmin(GuardedModelAdmin):
    list_display = ('name', )

@admin.register(Branch)
class BranchAdmin(GuardedModelAdmin):
    list_display = ('name', )