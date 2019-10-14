import threemf
import unittest
import io
import numpy as np

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
        writer = threemf.io.Writer()
        reader = threemf.io.Reader()
        
        with io.BytesIO() as f:
            writer.write(self.tmf, f)
            zip_bytes = f.getvalue()

        tmf2 = threemf.ThreeMF()

        with io.BytesIO(zip_bytes) as f:
            reader.read(tmf2, f)

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

class JsonAssetTest(unittest.TestCase):
    def setUp(self):
        self.tmf = threemf.ThreeMF()

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
