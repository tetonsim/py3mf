import threemf
import unittest
import io

class CubeTest(unittest.TestCase):
    def setUp(self):
        self.tmf = threemf.ThreeMF()

        c = threemf.geom.Cube(100., 100., 5.)

        self.cube = self.tmf.model_from_stl(c.stl_mesh())

        self.tmf.build.add_item(self.cube)

    def test_mesh(self):
        self.assertEqual( len(self.tmf.models), 1 )
        self.assertEqual( len(self.tmf.build.items) ,  1 )

        mesh = self.cube.mesh

        self.assertEqual( len(mesh.triangles), 12 )
        self.assertEqual( len(mesh.vertices), 36 )

    def test_meta_data(self):
        self.cube.add_meta_data_cura('infill_pattern', 'grid')
        self.cube.add_meta_data_cura('infill_sparse_density', 50)

        self.assertTrue('cura:infill_pattern' in self.cube.metadata.keys())
        self.assertTrue('cura:infill_sparse_density' in self.cube.metadata.keys())

        self.assertEqual(self.cube.metadata['cura:infill_pattern'], 'grid')
        self.assertEqual(self.cube.metadata['cura:infill_sparse_density'], 50)

    def test_threemf_write(self):
        writer = threemf.xml.Writer()

        with io.BytesIO() as f:
            writer.write(self.tmf, f)

        # for now, just assert that nothing is throwing an exception, however,
        # are their more explicit things we could check for in the file content?
