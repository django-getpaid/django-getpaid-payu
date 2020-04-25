from django.contrib import admin

from . import models


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "total",
        "currency",
        "status",
    )
