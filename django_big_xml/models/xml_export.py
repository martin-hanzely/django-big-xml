from __future__ import annotations
from uuid import uuid4

from django.db import models


def get_token() -> str:
    return str(uuid4())


def file_upload_path(instance: XMLExport, filename: str) -> str:
    return f"exports/xml/{filename}"


class XMLExport(models.Model):
    token = models.UUIDField(default=get_token, editable=False, unique=True)
    file = models.FileField(upload_to=file_upload_path, null=True, blank=True)
    compressed_file = models.FileField(upload_to=file_upload_path, null=True, blank=True)
    is_successful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        ordering = ["-pk"]
        get_latest_by = ["created_at"]
        indexes = [
            models.Index(fields=["token"], name="xml_export_token_idx"),
            models.Index(fields=["created_at"], name="xml_export_created_at_idx"),
        ]
