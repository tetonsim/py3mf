import sys
import stl
import numpy as np

class Vertex:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def transform(self, T):
        """
        TODO Re-examine this transformation. When combined with the
        Mesh.center method, it was making all y and z equal to 0.
        """
        X = np.multiply(T, np.matrix([[self.x], [self.y], [self.z], [1.0]]))
        self.x = X[0,0]
        self.y = X[1,0]
        self.z = X[2,0]

class Triangle:
    def __init__(self, v1=0, v2=0, v3=0):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3

class Mesh:
    def __init__(self):
        self.vertices = []
        self.triangles = []

    @classmethod
    def FromSTL(cls, stl_mesh):
        mesh = cls()

        for p in stl_mesh.points:
            vlen = len(mesh.vertices)

            for i in range(3):
                j = 3 * i
                mesh.vertices.append(Vertex(p[j], p[j + 1], p[j + 2]))

            mesh.triangles.append(Triangle(vlen, vlen + 1, vlen + 2))

        return mesh

    @classmethod
    def FromSTLFile(cls, stl_path):
        return cls.FromSTL( stl.mesh.Mesh.from_file(stl_path) )

    def bounding_box(self):
        pmin = Vertex(sys.float_info.max, sys.float_info.max, sys.float_info.max)
        pmax = Vertex(-sys.float_info.max, -sys.float_info.max, -sys.float_info.max)
        for v in self.vertices:
            pmin.x = min(pmin.x, v.x)
            pmin.y = min(pmin.y, v.y)
            pmin.z = min(pmin.z, v.z)
            pmax.x = max(pmax.x, v.x)
            pmax.y = max(pmax.y, v.y)
            pmax.z = max(pmax.z, v.z)

        return (pmin, pmax)

    def center(self):
        """
        Returns the transformation matrix that translates the center of the bounding box
        to (0, 0, 0).
        """

        box = self.bounding_box()

        T = np.identity(4)

        T[0,3] = -0.5 * (box[0].x + box[1].x)
        T[1,3] = -0.5 * (box[0].y + box[1].y)
        T[2,3] = -0.5 * (box[0].z + box[1].z)

        return T

    def transform(self, T):
        for v in self.vertices:
            v.transform(T)
