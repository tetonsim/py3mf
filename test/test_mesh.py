import numpy as np
import threemf
import unittest

def bounding_box(pmin: threemf.mesh.Vertex, pmax: threemf.mesh.Vertex) -> threemf.mesh.Mesh:
    v1 = np.array((pmax.x - pmin.x, 0., 0.))
    v2 = np.array((0., pmax.y - pmin.y, 0.))
    v3 = np.array((0., 0., pmax.z - pmin.z))

    p1 = np.array([pmin.x, pmin.y, pmin.z])
    pts = [p1, p1 + v1, p1 + v1 + v2, p1 + v2, p1 + v3, p1 + v1 + v3, p1 + v1 + v2 + v3, p1 + v2 + v3]

    conv = lambda arr: threemf.mesh.Vertex(arr[0], arr[1], arr[2])

    mesh = threemf.mesh.Mesh()
    mesh.vertices = [conv(p) for p in pts]

    tris = lambda A, B, C, D: (
            threemf.mesh.Triangle(A, B, D), threemf.mesh.Triangle(C, D, B)
        )
    mesh.triangles = [
        *tris(0, 3, 2, 1),
        *tris(0, 1, 5, 4),
        *tris(1, 2, 6, 5),
        *tris(2, 3, 7, 6),
        *tris(3, 0, 4, 7),
        *tris(4, 5, 6, 7)
    ]

    return mesh

class MeshesOperations(unittest.TestCase):
    def test_add_meshes(self):
        p1min = threemf.mesh.Vertex(0, 0, 0)
        p1max = threemf.mesh.Vertex(1., 1., 1.)
        box1 = bounding_box(p1min, p1max)

        p2min = threemf.mesh.Vertex(2, 0, 0)
        p2max = threemf.mesh.Vertex(3., 1., 1.)
        box2 = bounding_box(p2min, p2max)

        c_mesh = box1 + box2

        self.assertEqual(len(c_mesh.vertices), 16)
        self.assertEqual(len(c_mesh.triangles), 24)

        p3min = threemf.mesh.Vertex(1, 1, 1)
        p3max = threemf.mesh.Vertex(2., 2., 2.)
        box3 = bounding_box(p3min, p3max)

        c_mesh = box1 + box3

        self.assertEqual(len(c_mesh.vertices), 15)
        self.assertEqual(len(c_mesh.triangles), 24)

        c_mesh = c_mesh + box2

        self.assertEqual(len(c_mesh.vertices), 22)
        self.assertEqual(len(c_mesh.triangles), 36)

    def test_mesh_to_stl(self):
        p1min = threemf.mesh.Vertex(0, 0, 0)
        p1max = threemf.mesh.Vertex(1., 1., 1.)
        box1 = bounding_box(p1min, p1max)

        stl_mesh = box1.to_stl()

        self.assertEqual(len(stl_mesh.vectors), 12)
