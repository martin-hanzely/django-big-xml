from __future__ import annotations
import zipfile
from io import BytesIO
from typing import TYPE_CHECKING, Optional
from xml.sax.saxutils import XMLGenerator

from django.core import files
from django.forms.models import model_to_dict

from django_big_xml.models import XMLExport

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


class _XMLGenerator(XMLGenerator):
    """
    Simple XML generator helper class.
    """
    def write_element(self, tag: str, text: str = "", attrs: Optional[dict] = None) -> None:
        self.startElement(tag, attrs or {})
        self.characters(text)
        self.endElement(tag)


class XMLSerializer:
    _file: BytesIO
    _xml_generator: _XMLGenerator
    _object_element_title: str = "item"
    _list_element_title: str = "items"

    def __init__(self) -> None:
        self._file = BytesIO()
        self._xml_generator = _XMLGenerator(self._file, "UTF-8", short_empty_elements=True)

    def start_document(self) -> None:
        self._xml_generator.startDocument()

    def end_document(self) -> None:
        self._xml_generator.endDocument()

    def serialize_queryset(self, queryset: QuerySet) -> None:
        self.start_document()
        self._xml_generator.startElement(self._list_element_title, {})

        for item in queryset.all():
            self._xml_generator.write_element(
                self._object_element_title,
                attrs={k: str(v) for k, v in model_to_dict(item).items()},
            )

        self._xml_generator.endElement(self._list_element_title)
        self.end_document()

    def generate_xml_export(self, queryset: QuerySet) -> XMLExport:
        xml_export = XMLExport.objects.create(is_successful=False)

        # Serialize queryset to XML.
        self.serialize_queryset(queryset)

        # Save XML to file.
        xml_export.file.save(f"{xml_export.token}.xml", files.File(self._file))

        # Save compressed XML to zip file.
        zip_file = BytesIO()
        with zipfile.ZipFile(zip_file, "a", zipfile.ZIP_DEFLATED, compresslevel=5) as buffer:
            buffer.writestr(f"{xml_export.token}.xml", self._file.getvalue())
        xml_export.compressed_file.save(f"{xml_export.token}.zip", files.File(zip_file))

        # Mark as successful.
        xml_export.is_successful = True

        xml_export.save(update_fields=["file", "compressed_file", "is_successful"])
        return xml_export
