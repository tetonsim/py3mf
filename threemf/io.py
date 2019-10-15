import zipfile
import typing
import xml.etree.cElementTree as xml

from . import ThreeMF

class Writer:
    def write(self, tmf : ThreeMF, tmffile : typing.io.BinaryIO):
        """
            tmf: ThreeMF object
            tmffile: file like object
        """

        z = zipfile.ZipFile(tmffile, mode='w', compression=zipfile.ZIP_DEFLATED)

        z.writestr(tmf._CONTENT_TYPES_PATH, xml.tostring(tmf._content_types_xml, encoding='utf8'))
        z.writestr(tmf._RELS_PATH, xml.tostring(tmf._relationships_xml, encoding='utf8'))

        for m in tmf.models:
            z.writestr(m.path, xml.tostring(m.serialize(), encoding='utf8'))

        for ext in tmf.extensions:
            ext.write(z)

        z.close()

class Reader:
    def __init__(self):
        self._extensions = []

    def register_extension(self, cls):
        self._extensions.append(cls)

    def read(self, tmf : ThreeMF, tmffile : typing.io.BinaryIO):
        z = zipfile.ZipFile(tmffile)

        content_types_xml = z.read(tmf._CONTENT_TYPES_PATH).decode('utf-8')
        relationships_xml = z.read(tmf._RELS_PATH).decode('utf-8')

        tmf._load(
            z,
            content_types_xml,
            relationships_xml
        )

        for ext in self._extensions:
            tmf.extensions.append(ext.read(z))

        for ext in tmf.extensions:
            ext.process_threemf(tmf)
