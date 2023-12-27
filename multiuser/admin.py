from django.contrib import admin
from django.contrib import admin
from .models import *

admin.site.register(Organisation)
admin.site.register(Business)
admin.site.register(Branch)
admin.site.register(OrganisationAssignment)
admin.site.register(BusinessAssignment)
admin.site.register(BranchAssignment)