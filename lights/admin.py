from django.contrib import admin

from . import models


@admin.register(models.Lamp)
class LampAdmin(admin.ModelAdmin):

    list_display = ('name', 'is_on', 'brightness')
    ordering = ('name',)
