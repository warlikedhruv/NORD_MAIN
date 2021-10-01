from django.contrib import admin
from .models import Tenant
# Register your models here.

class TenantAdmin(admin.ModelAdmin):
    search_fields=('organisation_name',)
    list_display=['organisation_name','organization_address']
    list_filter=['organisation_name','organisation_size']

admin.site.register(Tenant,TenantAdmin)