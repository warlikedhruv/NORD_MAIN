from django.contrib import admin

# Register your models here.
from .models import Document,PrivateAccess

class DocumentAdmin(admin.ModelAdmin):
    search_fields=('document_name',)
    list_display=['document_name','doc_type']
    list_filter=['document_name','doc_type']

class PrivateAccessAdmin(admin.ModelAdmin):
    list_filter=['doc','access_tenant']

admin.site.register(Document,DocumentAdmin)
admin.site.register(PrivateAccess,PrivateAccessAdmin)