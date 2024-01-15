from django.contrib import admin
from .models import *
from guardian.admin import GuardedModelAdmin

@admin.register(Entity)
class EntityAdmin(GuardedModelAdmin):
    pass

@admin.register(Organisation)
class OrganisationAdmin(GuardedModelAdmin):
    pass

@admin.register(Business)
class BusinessAdmin(GuardedModelAdmin):
    pass

@admin.register(Branch)
class BranchAdmin(GuardedModelAdmin):
    pass
