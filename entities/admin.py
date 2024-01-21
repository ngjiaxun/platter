from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from .models import Entity

@admin.register(Entity)
class EntityAdmin(GuardedModelAdmin):
    pass