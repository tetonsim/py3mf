import os
import setuptools

from threemf import __version__

build_num = os.getenv('BUILD_NUMBER')

if build_num:
    version += '.' + str(build_num)

setuptools.setup(
    name='teton-3mf',
    version=__version__,
    author='Teton Simulation',
    author_email='info@tetonsim.com',
    packages=setuptools.find_packages(),
    install_requires=['numpy', 'numpy-stl'],
    license='LGPLv3'
)
