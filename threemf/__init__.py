import numpy as np
import stl

from . import geom, mesh, xml

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

class Model(Object):
    def __init__(self, id):
        super().__init__(id, 'model')

        self.mesh = mesh.Mesh()
        self.metadata = {}

    def add_meta_data(self, name, value):
        if not name.startswith('cura:'):
            name = 'cura:' + name
        self.metadata[name] = value

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
