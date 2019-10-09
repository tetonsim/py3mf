
class Extension:
    '''
    The base class for defining an extension to the ThreeMF
    '''

    Name = None

class DirectoryExtension(Extension):
    Directory = None

    def read(self, todo):
        raise NotImplementedError()

    def write(self, todo):
        raise NotImplementedError()

class CuraDirectory(DirectoryExtension):
    Name = 'Cura'
