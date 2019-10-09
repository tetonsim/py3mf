import stl
import numpy as np
import xml.etree.cElementTree as xml

from . import mesh

class BuildItem:
    def __init__(self, objectid, transform=None):
        self.objectid = objectid
        self.transform = transform if transform is not None else np.identity(4)

class Build:
    def __init__(self):
        self.items = []

    def add_item(self, obj, transform=None):
        self.items.append(
            BuildItem(obj.id, transform)
        )

class Object:
    def __init__(self, id, type):
        self.id = id
        self.type = type

class ObjectModel(Object):
    def __init__(self, id):
        super().__init__(id, 'model')

        self.mesh = mesh.Mesh()
        self.metadata = {}

    def add_meta_data(self, name, value):
        self.metadata[name] = value

    def add_meta_data_cura(self, name, value):
        if not name.startswith('cura:'):
            name = 'cura:' + name
        self.metadata[name] = value

class Model:
    def __init__(self, path):
        self.path = path
        self.objects = []
        self.build = Build()
        self.unit = 'millimeter'

        self._next_object_id = 1

    def object_from_stl_file(self, stl_path):
        mdl = ObjectModel(self._next_object_id)
        mdl.mesh = mesh.Mesh.FromSTLFile(stl_path)
        
        self._next_object_id += 1

        self.objects.append(mdl)

        return mdl

    def object_from_stl(self, stl_mesh : stl.mesh.Mesh):
        mdl = ObjectModel(self._next_object_id)
        mdl.mesh = mesh.Mesh.FromSTL(stl_mesh)
        
        self._next_object_id += 1

        self.objects.append(mdl)

        return mdl

    def serialize(self):
        root = xml.Element('model')

        root.set('unit', self.unit)
        root.set('xmlns', 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02')
        root.set('xmlns:cura', 'http://software.ultimaker.com/xml/cura/3mf/2015/10')
        root.set('xml:lang', 'en-US')

        resources = xml.Element('resources')

        for obj in self.objects:
            if isinstance(obj, ObjectModel):
                resources.append(self._model(obj))
            else:
                raise Exception(f'Unsupported object type: {obj.type}')

        root.append(resources)
        root.append(self._build())

        return xml.tostring(root, encoding='utf8')

    def _model(self, model):
        obj = xml.Element('object')
        obj.set('id', str(model.id))
        obj.set('type', model.type)

        mesh = xml.Element('mesh')
        verts = xml.Element('vertices')
        tris = xml.Element('triangles')

        for v in model.mesh.vertices:
            xv = xml.Element('vertex')
            xv.set('x', str(v.x))
            xv.set('y', str(v.y))
            xv.set('z', str(v.z))

            verts.append(xv)

        for t in model.mesh.triangles:
            xt = xml.Element('triangle')
            xt.set('v1', str(t.v1))
            xt.set('v2', str(t.v2))
            xt.set('v3', str(t.v3))

            tris.append(xt)

        mesh.append(verts)
        mesh.append(tris)

        obj.append(mesh)

        if len(model.metadata) > 0:
            metadatagroup = xml.Element('metadatagroup')
            for k, v in model.metadata.items():
                xm = xml.Element('metadata')
                xm.set('name', k)
                xm.set('preserve', 'true')
                xm.set('type', 'xs:string')
                xm.text = str(v)

                metadatagroup.append(xm)
            
            obj.append(metadatagroup)

        return obj

    def _build(self):
        b = xml.Element('build')

        for item in self.build.items:
            b.append(self._build_item(item))

        return b

    def _build_item(self, item):
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

        return xi
