import threemf
import unittest
import io
import numpy as np

def write_and_read(tmf: threemf.ThreeMF) -> threemf.ThreeMF:
    writer = threemf.io.Writer()
    reader = threemf.io.Reader()

    with io.BytesIO() as f:
        writer.write(tmf, f)
        zip_bytes = f.getvalue()

    tmf2 = threemf.ThreeMF()

    with io.BytesIO(zip_bytes) as f:
        reader.read(tmf2, f)

    return tmf2

class CubeTest(unittest.TestCase):
    def setUp(self):
        self.tmf = threemf.ThreeMF()

        c = threemf.geom.Cube(100., 100., 5.)

        self.cube = self.tmf.default_model.object_from_stl(c.stl_mesh())

        self.cube.add_meta_data_cura('infill_pattern', 'grid')
        self.cube.add_meta_data_cura('infill_sparse_density', 50)

        self.cubeT = np.array(
            [
                [0.3, 0.7, 0.0, 10.],
                [0.4, 0.5, 0.1, 11.],
                [0.2, 0.2, 0.6, 12.],
                [0.0, 0.0, 0.0, 1.0]
            ]
        )

        self.tmf.default_model.build.add_item(self.cube, self.cubeT)

    def test_mesh(self):
        self.assertEqual( len(self.tmf.models), 1 )
        self.assertEqual( len(self.tmf.default_model.objects), 1 )
        self.assertEqual( len(self.tmf.default_model.build.items) ,  1 )

        mesh = self.cube.mesh

        self.assertEqual( len(mesh.triangles), 12 )
        self.assertEqual( len(mesh.vertices), 36 )

    def test_meta_data(self):
        self.assertTrue(self.cube.has_meta_data('cura:infill_pattern'))
        self.assertTrue(self.cube.has_meta_data('cura:infill_sparse_density'))

        self.assertEqual(self.cube.get_meta_data('cura:infill_pattern').value, 'grid')
        self.assertEqual(self.cube.get_meta_data('cura:infill_sparse_density').value, '50')

    def test_threemf_write(self):
        tmf2 = write_and_read(self.tmf)

        self.assertEqual( len(tmf2.models), 1 )
        self.assertEqual( len(tmf2.models[0].objects), 1 )
        self.assertEqual( len(tmf2.models[0].build.items) ,  1 )

        mdl = tmf2.models[0].objects[0]
        mesh = mdl.mesh

        self.assertEqual( len(mesh.triangles), 12 )
        self.assertEqual( len(mesh.vertices), 36 )

        item = tmf2.models[0].build.items[0]

        self.assertEqual(item.objectid, mdl.id)
        self.assertTrue(np.array_equal(item.transform, self.cubeT))

        self.assertTrue(mdl.has_meta_data('cura:infill_pattern'))
        self.assertTrue(mdl.has_meta_data('cura:infill_sparse_density'))

        self.assertEqual(mdl.get_meta_data('cura:infill_pattern').value, 'grid')
        self.assertEqual(int(mdl.get_meta_data('cura:infill_sparse_density').value), 50)

class TestExtension(threemf.extension.Extension):
    Name = 'TestExtension'

    def __init__(self):
        super().__init__(TestExtension.Name)

    def process_threemf(self, tmf : threemf.ThreeMF):
        content = self.assets[0].content
        mesh = tmf.default_model.objects[0].mesh
        content['num_tris'] = len(mesh.triangles)

class JsonAssetTest(unittest.TestCase):
    def setUp(self):
        self.tmf = threemf.ThreeMF()

        mdl = self.tmf.default_model

        c = threemf.geom.Cube(10., 10., 5.)
        self.cube = self.tmf.default_model.object_from_stl(c.stl_mesh())
        self.tmf.default_model.build.add_item(self.cube)

        self.ext = TestExtension()

        jasset = threemf.extension.JsonFile('test.json')
        jasset.content = {
            'name': 'my extension\'s file',
            'mass': 258.1
        }

        self.ext.assets.append(jasset)

        self.tmf.extensions.append(self.ext)

    def test_json_asset(self):
        writer = threemf.io.Writer()
        reader = threemf.io.Reader()

        reader.register_extension(TestExtension)

        with io.BytesIO() as f:
            writer.write(self.tmf, f)
            zip_bytes = f.getvalue()

        tmf2 = threemf.ThreeMF()

        with io.BytesIO(zip_bytes) as f:
            reader.read(tmf2, f)

        self.assertEqual(len(tmf2.extensions), 1)
        self.assertEqual(len(tmf2.extensions[0].assets), 1)

        asset = tmf2.extensions[0].assets[0]

        self.assertTrue(isinstance(asset.content, dict))
        self.assertEqual(asset.content['name'], "my extension's file")
        self.assertEqual(asset.content['mass'], 258.1)

        self.assertTrue('num_tris' in asset.content.keys())
        self.assertEqual(asset.content['num_tris'], 12)


class ComponentTest(unittest.TestCase):
    def test_cube_in_cube(self):
        self.tmf = threemf.ThreeMF()

        c1 = threemf.geom.Cube(100., 100., 5.)
        c2 = threemf.geom.Cube(20., 20., 3.)

        self.cube1 = self.tmf.default_model.object_from_stl(c1.stl_mesh())
        self.cube2 = self.tmf.default_model.object_from_stl(c2.stl_mesh())

        cos45 = 0.7071
        sin45 = 0.7071

        self.componentT = np.array(
            [
                [cos45, -sin45, 0.0, 40.0],
                [sin45, cos45, 0.0, 40.0],
                [0.0, 0.0, 1.0, 1.0],
                [0.0, 0.0, 0.0, 1.0]
            ]
        )

        self.cube1.add_component(self.cube2, self.componentT)

        self.tmf.default_model.build.add_item(self.cube1)

        tmf2 = write_and_read(self.tmf)

        objs = tmf2.default_model.objects
        build = tmf2.default_model.build

        self.assertEqual(len(objs), 2)
        self.assertEqual(len(build.items), 1)

        main_obj_id = build.items[0].objectid

        self.assertEqual(main_obj_id, self.cube1.id)

        main_obj = next(o for o in objs if o.id == main_obj_id)

        self.assertEqual(len(main_obj.components), 1)

        component = main_obj.components[0]

        self.assertEqual(component.objectid, self.cube2.id)
        self.assertTrue(np.array_equal(component.transform, self.componentT))


