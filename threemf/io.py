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

        z.close()
