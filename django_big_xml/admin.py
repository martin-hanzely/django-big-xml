from django.contrib import admin

from django_big_xml.models import XMLExport


@admin.register(XMLExport)
class XMLExportAdmin(admin.ModelAdmin):
    list_display = ["pk", "token", "file", "compressed_file", "is_successful", "created_at"]
