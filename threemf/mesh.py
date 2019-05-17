import stl

class Vertex:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

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
