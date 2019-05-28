import os
import setuptools

version = '19.0.1'

build_num = os.getenv('BUILD_NUMBER')

if build_num:
    version += '.' + str(build_num)

setuptools.setup(
    name='threemf',
    version=version,
    author='Teton Simulation',
    author_email='info@tetonsim.com',
    packages=setuptools.find_packages(),
    install_requires=['numpy', 'numpy-stl']
)
