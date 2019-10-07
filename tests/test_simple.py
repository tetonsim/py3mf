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
        pass

    def test_meta_data(self):
        self.cube.add_meta_data('infill_pattern', 'grid')
        self.cube.add_meta_data('infill_sparse_density', 50)

    def test_threemf_write(self):
        writer = threemf.xml.Writer()

        with io.BytesIO() as f:
            writer.write(self.tmf, f)
