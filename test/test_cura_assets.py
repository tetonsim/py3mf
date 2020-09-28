import threemf
import unittest
import io
import json

class CuraAssetTest(unittest.TestCase):
    def setUp(self):
        self.tmf = threemf.ThreeMF()

        cura_ext = threemf.extension.Cura()

        cura_asset = threemf.extension.RawFile('printer.def.json')
        cura_asset.content = json.dumps(
            { 'test': 100 }
        )

        cura_ext.assets.append(cura_asset)

        self.tmf.extensions.append(cura_ext)

    def test_recover_assets(self):
        writer = threemf.io.Writer()
        reader = threemf.io.Reader()

        cura_ext = reader.register_extension(threemf.extension.Cura)

        with io.BytesIO() as f:
            writer.write(self.tmf, f)
            zip_bytes = f.getvalue()

        tmf2 = threemf.ThreeMF()

        with io.BytesIO(zip_bytes) as f:
            reader.read(tmf2, f)

        self.assertEqual(len(tmf2.extensions), 1)
        self.assertEqual(cura_ext.Name, 'Cura')
        self.assertEqual(len(cura_ext.assets), 1)

        content = json.loads(cura_ext.assets[0].content.decode('utf-8'))

        self.assertEqual(len(content.keys()), 1)
        self.assertEqual(content['test'], 100)
