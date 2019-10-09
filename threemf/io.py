import zipfile

#from . import ThreeMF, Model, Build, BuildItem

class Writer:
    def write(self, tmf, tmffile):
        """
            tmf: ThreeMF object
            tmffile: file like object
        """

        z = zipfile.ZipFile(tmffile, mode='w', compression=zipfile.ZIP_DEFLATED)

        z.writestr('[Content_Types].xml', tmf.content_types.serialize())
        z.writestr('_rels/.rels', tmf.relationships.serialize())

        for m in tmf.models:
            z.writestr(m.path, m.serialize())

        for ext in tmf.extensions:
            ext.write(z)

        z.close()

class Reader:
    def __init__(self):
        self._extensions = []

    def register_extension(self, cls):
        self._extensions.append(cls)

    def read(self, tmf, tmffile):
        z = zipfile.ZipFile(tmffile)

        for ext in self._extensions:
            tmf.extensions.append(ext.read(z))
