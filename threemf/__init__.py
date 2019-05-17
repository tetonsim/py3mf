import numpy as np
import stl
import zipfile
import xml.etree.cElementTree as xml

from . import mesh

class BuildItem:
    def __init__(self, objectid, transform=None):
        self.objectid = objectid
        self.transform = transform if transform else np.identity(4)

class Build:
    def __init__(self):
        self.items = []

    def add_item(self, obj, transform=None):
        self.items.append(
            BuildItem(obj.id, transform)
        )

    def to_xml(self):
        b = xml.Element('build')

        for item in self.items:
            xi = xml.Element('item')
            xi.set('objectid', str(item.objectid))

            # Transpose the transformation matrix (3MF uses row-major)
            # https://github.com/3MFConsortium/spec_core/blob/master/3MF%20Core%20Specification.md#33-3d-matrices
            flatt = item.transform.transpose().tolist()

            # flatt contains a list of rows - loop through the rows and then
            # the first 3 columns and put into a flattened list
            comp_strings = [str(c) for row in flatt for c in row[0:3]]

            # Create the attribute string as a space separated list of the matrix values
            transform_string = ' '.join(comp_strings)

            xi.set('transform', transform_string)

            b.append(xi)

        return b

class Object:
    def __init__(self, id, type):
        self.id = id
        self.type = type

class Model(Object):
    def __init__(self, id):
        super().__init__(id, 'model')

        self.mesh = mesh.Mesh()
        self.metadata = {}

    def add_meta_data(self, name, value):
        if not name.startswith('cura:'):
            name = 'cura:' + name
        self.metadata[name] = value

    def to_xml(self):
        obj = xml.Element('object')
        obj.set('id', str(self.id))
        obj.set('type', self.type)

        mesh = xml.Element('mesh')
        verts = xml.Element('vertices')
        tris = xml.Element('triangles')

        for v in self.mesh.vertices:
            xv = xml.Element('vertex')
            xv.set('x', str(v.x))
            xv.set('y', str(v.y))
            xv.set('z', str(v.z))

            verts.append(xv)

        for t in self.mesh.triangles:
            xt = xml.Element('triangle')
            xt.set('v1', str(t.v1))
            xt.set('v2', str(t.v2))
            xt.set('v3', str(t.v3))

            tris.append(xt)

        mesh.append(verts)
        mesh.append(tris)

        obj.append(mesh)

        if len(self.metadata) > 0:
            metadatagroup = xml.Element('metadatagroup')
            for k, v in self.metadata.items():
                xm = xml.Element('metadata')
                xm.set('name', k)
                xm.set('preserve', 'true')
                xm.set('type', 'xs:string')
                xm.text = str(v)

                metadatagroup.append(xm)
            
            obj.append(metadatagroup)

        return obj

class ThreeMF:
    _THREED_MODEL_PATH = '3D/3dmodel.model'

    def __init__(self):
        self.models = []
        self.build = Build()
        self.unit = 'millimeter'

        self._next_object_id = 1

    def model_from_stl_file(self, stl_path):
        mdl = Model(self._next_object_id)
        mdl.mesh = mesh.Mesh.FromSTLFile(stl_path)
        
        self._next_object_id += 1

        self.models.append(mdl)

        return mdl

    def model_from_stl(self, stl_mesh : stl.mesh.Mesh):
        mdl = Model(self._next_object_id)
        mdl.mesh = mesh.Mesh.FromSTL(stl_mesh)
        
        self._next_object_id += 1

        self.models.append(mdl)

        return mdl

    def to_xml(self):
        root = xml.Element('model')

        root.set('unit', self.unit)
        root.set('xmlns', 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02')
        root.set('xmlns:cura', 'http://software.ultimaker.com/xml/cura/3mf/2015/10')
        root.set('xml:lang', 'en-US')

        resources = xml.Element('resources')

        for m in self.models:
            resources.append(m.to_xml())

        root.append(resources)
        root.append(self.build.to_xml())

        return xml.ElementTree(root)

    def _content_types_xml(self):
        # I'm honestly not sure what this file is for and I directly
        # copied the content from an example 3MF written by Cura. This
        # may need to change, if it in fact, depends on other information.

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

        return xml.ElementTree(root)

    def _relationships_xml(self):
        # I'm honestly not sure what this file is for and I directly
        # copied the content from an example 3MF written by Cura. This
        # may need to change, if it in fact, depends on other information.

        root = xml.Element('Relationships')

        root.set('xmlns', 'http://schemas.openxmlformats.org/package/2006/relationships')

        rel1 = xml.Element('Relationship')
        rel1.set('Id', 'rel0')
        rel1.set('Target', ThreeMF._THREED_MODEL_PATH)
        rel1.set('Type', 'http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')

        root.append(rel1)

        return xml.ElementTree(root)

    def write(self, tmffile):
        """
            tmffile: file like object
        """

        content_types = self._content_types_xml()
        relationships = self._relationships_xml()
        modelxml = self.to_xml()

        z = zipfile.ZipFile(tmffile, mode='w', compression=zipfile.ZIP_DEFLATED)

        z.writestr('[Content_Types].xml', xml.tostring(content_types.getroot(), encoding='utf8'))
        z.writestr('_rels/.rels', xml.tostring(relationships.getroot(), encoding='utf8'))
        z.writestr(ThreeMF._THREED_MODEL_PATH, xml.tostring(modelxml.getroot(), encoding='utf8'))

        z.close()
