import zipfile
import xml.etree.cElementTree as xmltree

#from . import ThreeMF, Model, Build, BuildItem

class Writer:
    def write(self, tmf, tmffile):
        """
            tmf: ThreeMF object
            tmffile: file like object
        """

        content_types = self._content_types(tmf)
        relationships = self._relationships(tmf)
        modelxml = self._threemf(tmf)

        z = zipfile.ZipFile(tmffile, mode='w', compression=zipfile.ZIP_DEFLATED)

        z.writestr('[Content_Types].xml', xmltree.tostring(content_types.getroot(), encoding='utf8'))
        z.writestr('_rels/.rels', xmltree.tostring(relationships.getroot(), encoding='utf8'))
        z.writestr(tmf._THREED_MODEL_PATH, xmltree.tostring(modelxml.getroot(), encoding='utf8'))

        z.close()

    def _content_types(self, tmf):
        # I'm honestly not sure what this file is for and I directly
        # copied the content from an example 3MF written by Cura. This
        # may need to change, if it in fact, depends on other information.

        root = xmltree.Element('Types')

        root.set('xmlns', 'http://schemas.openxmlformats.org/package/2006/content-types')

        def1 = xmltree.Element('Default')
        def1.set('ContentType', 'application/vnd.openxmlformats-package.relationships+xml')
        def1.set('Extension', 'rels')
        
        def2 = xmltree.Element('Default')
        def2.set('ContentType', 'application/vnd.ms-package.3dmanufacturing-3dmodel+xml')
        def2.set('Extension', 'model')

        root.append(def1)
        root.append(def2)

        return xmltree.ElementTree(root)

    def _relationships(self, tmf):
        # I'm honestly not sure what this file is for and I directly
        # copied the content from an example 3MF written by Cura. This
        # may need to change, if it in fact, depends on other information.

        root = xmltree.Element('Relationships')

        root.set('xmlns', 'http://schemas.openxmlformats.org/package/2006/relationships')

        rel1 = xmltree.Element('Relationship')
        rel1.set('Id', 'rel0')
        rel1.set('Target', tmf._THREED_MODEL_PATH)
        rel1.set('Type', 'http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')

        root.append(rel1)

        return xmltree.ElementTree(root)


    def _threemf(self, tmf):
        root = xmltree.Element('model')

        root.set('unit', tmf.unit)
        root.set('xmlns', 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02')
        root.set('xmlns:cura', 'http://software.ultimaker.com/xml/cura/3mf/2015/10')
        root.set('xml:lang', 'en-US')

        resources = xmltree.Element('resources')

        for m in tmf.models:
            resources.append(self._model(m))

        root.append(resources)
        root.append(self._build(tmf.build))

        return xmltree.ElementTree(root)

    def _model(self, model):
        obj = xmltree.Element('object')
        obj.set('id', str(model.id))
        obj.set('type', model.type)

        mesh = xmltree.Element('mesh')
        verts = xmltree.Element('vertices')
        tris = xmltree.Element('triangles')

        for v in model.mesh.vertices:
            xv = xmltree.Element('vertex')
            xv.set('x', str(v.x))
            xv.set('y', str(v.y))
            xv.set('z', str(v.z))

            verts.append(xv)

        for t in model.mesh.triangles:
            xt = xmltree.Element('triangle')
            xt.set('v1', str(t.v1))
            xt.set('v2', str(t.v2))
            xt.set('v3', str(t.v3))

            tris.append(xt)

        mesh.append(verts)
        mesh.append(tris)

        obj.append(mesh)

        if len(model.metadata) > 0:
            metadatagroup = xmltree.Element('metadatagroup')
            for k, v in model.metadata.items():
                xm = xmltree.Element('metadata')
                xm.set('name', k)
                xm.set('preserve', 'true')
                xm.set('type', 'xs:string')
                xm.text = str(v)

                metadatagroup.append(xm)
            
            obj.append(metadatagroup)

        return obj

    def _build(self, build):
        b = xmltree.Element('build')

        for item in build.items:
            b.append(self._build_item(item))

        return b

    def _build_item(self, item):
        xi = xmltree.Element('item')
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
