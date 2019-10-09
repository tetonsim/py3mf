import xml.etree.cElementTree as xml
from io import StringIO

class ThreeMF:
    _THREED_MODEL_PATH = '3D/3dmodel.model'
    _CONTENT_TYPES_PATH = '[Content_Types].xml'
    _RELS_PATH = '_rels/.rels'

    def __init__(self):
        self.models = []
        self.extensions = []

        #self.content_types = ContentTypes()
        #self.relationships = Relationships(self.models)

    @property
    def default_model(self):
        for m in self.models:
            if m.path == ThreeMF._THREED_MODEL_PATH:
                return m
        
        new_mdl = model.Model(ThreeMF._THREED_MODEL_PATH)
        self.models.append(new_mdl)
        
        return new_mdl

    @property
    def _relationships_xml(self):
        root = xml.Element('Relationships')

        root.set('xmlns', 'http://schemas.openxmlformats.org/package/2006/relationships')

        for m in self.models:
            rel = xml.Element('Relationship')
            rel.set('Id', 'rel0')
            rel.set('Target', m.path)
            rel.set('Type', 'http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')

            root.append(rel)

        return xml.tostring(root, encoding='utf8')

    @property
    def _content_types_xml(self):        
        root = xml.Element('Types')

        root.set('xmlns', 'http://schemas.openxmlformats.org/package/2006/content-types')

        def1 = xml.Element('Default')
        def1.set('ContentType', 'application/vnd.openxmlformats-package.relationships+xml')
        def1.set('Extension', 'rels')
        
        def2 = xml.Element('Default')
        def2.set('ContentType', 'application/vnd.ms-package.3dmanufacturing-3dmodel+xml')
        def2.set('Extension', 'model')

        # TODO write extensions here?

        root.append(def1)
        root.append(def2)

        return xml.tostring(root, encoding='utf8')

    def _load(self, zipf, rels_xml, ct_xml):
        # TODO load extensions from content types XML?

        it = xml.iterparse(StringIO(rels_xml))
        for _, el in it:
            prefix, has_namespace, postfix = el.tag.partition('}')
            if has_namespace:
                el.tag = postfix  # strip all namespaces
        root = it.root

        model_paths = []
        for rel in root.findall('Relationship'):
            if rel.get('Type').endswith('3dmodel'):
                model_paths.append( rel.get('Path') )

        # for each model path create a new Model object and add it to models        

from . import extension, geom, mesh, model, io
