import os
import zipfile

class Asset:
    def __init__(self, name):
        self.name = name

    def serialize(self):
        raise NotImplementedError

class RawFile(Asset):
    def __init__(self, name):
        super().__init__(name)
        self.content = ''

    def serialize(self):
        return self.content

class Extension:
    '''
    The base class for defining an extension to the ThreeMF
    '''

    Name = None

    def __init__(self, directory):
        self.directory = directory
        self.assets = []

    def write(self, zipf : zipfile.ZipFile):
        for asset in self.assets:
            zipf.writestr(os.path.join(self.directory, asset.name), asset.serialize())

    @classmethod
    def read(cls, zipf : zipfile.ZipFile):
        '''
        The default read method will read all files in the Extension's
        directory as RawFile assets.
        '''
        ext = cls()

        dir_with_sep = ext.directory + os.sep

        for f in zipf.namelist():
            if f.startswith(dir_with_sep):
                asset = RawFile(f.lstrip(dir_with_sep))
                asset.content = zipf.read(f)
                ext.assets.append(asset)

        return ext

class Cura(Extension):
    '''
    This extension is for maintaining the files from the Cura
    directory, if it exists. Currently, the files are not parsed,
    only stored in memory so they can be restored when the 3MF is
    written back to a file.
    '''

    Name = 'Cura'

    def __init__(self):
        super().__init__(Cura.Name)
