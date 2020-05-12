from django.contrib import admin

from apps.models import APPModel

# Register your models here.


@admin.register(APPModel)
class APPAdminModel(admin.ModelAdmin):
    pass
