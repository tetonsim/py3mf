import xml.etree.cElementTree as xml

from . import extension, geom, mesh, model, io

class ThreeMF:
    _THREED_MODEL_PATH = '3D/3dmodel.model'

    def __init__(self):
        self.models = []
        self.extensions = []

        self.content_types = ContentTypes()
        self.relationships = Relationships(self.models)

    @property
    def default_model(self):
        for m in self.models:
            if m.path == ThreeMF._THREED_MODEL_PATH:
                return m
        
        new_mdl = model.Model(ThreeMF._THREED_MODEL_PATH)
        self.models.append(new_mdl)
        
        return new_mdl

class ContentTypes:
    def serialize(self):        
        root = xml.Element('Types')

        root.set('xmlns', 'http://schemas.openxmlformats.org/package/2006/content-types')

        def1 = xml.Element('Default')
        def1.set('ContentType', 'application/vnd.openxmlformats-package.relationships+xml')
        def1.set('Extension', 'rels')
        
        def2 = xml.Element('Default')
        def2.set('ContentType', 'application/vnd.ms-package.3dmanufacturing-3dmodel+xml')
        def2.set('Extension', 'model')

        root.append(def1)
        root.append(def2)

        return xml.tostring(root, encoding='utf8')

class Relationships:
    def __init__(self, models):
        self._models = models

    def serialize(self):
        # I'm honestly not sure what this file is for and I directly
        # copied the content from an example 3MF written by Cura. This
        # may need to change, if it in fact, depends on other information.

        root = xml.Element('Relationships')

        root.set('xmlns', 'http://schemas.openxmlformats.org/package/2006/relationships')

        for m in self._models:
            rel = xml.Element('Relationship')
            rel.set('Id', 'rel0')
            rel.set('Target', m.path)
            rel.set('Type', 'http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')

            root.append(rel)

        return xml.tostring(root, encoding='utf8')
