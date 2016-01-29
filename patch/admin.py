from django.contrib import admin
from models import Patch


class PatchAdmin(admin.ModelAdmin):
    pass

admin.site.register(Patch, PatchAdmin)
