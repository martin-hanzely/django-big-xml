from __future__ import annotations
from typing import TYPE_CHECKING

from django.contrib import admin, messages
from django.utils.html import format_html

from django_big_xml.models import Item, XMLExport
from django_big_xml.serializer import XMLSerializer

if TYPE_CHECKING:
    from django.http import HttpRequest
    from django.db.models.query import QuerySet


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "created_at")

    actions = ("generate_xml_export",)

    @admin.display(description="Generate XML export")
    def generate_xml_export(self, request: HttpRequest, queryset: QuerySet) -> None:
        serializer = XMLSerializer()
        xml_export = serializer.generate_xml_export(queryset)
        if xml_export.is_successful:
            self.message_user(
                request,
                format_html(
                    "<a href=\"{}\">XML export</a> has been generated.",
                    xml_export.get_admin_url(),
                ),
                messages.SUCCESS,
            )
        else:
            self.message_user(request, "Failed to generate XML export.", messages.ERROR)


@admin.register(XMLExport)
class XMLExportAdmin(admin.ModelAdmin):
    list_display = ["pk", "token", "file", "compressed_file", "is_successful", "created_at"]
