from setuptools import setup, find_packages
import os

# single source of truth for package version
version_ns = {}
with open(os.path.join("materials_io", "version.py")) as f:
    exec(f.read(), version_ns)
version = version_ns['__version__']

setup(
    name="materials_io",
    version=version,
    packages=find_packages(include=['materials_io*']) + ['materials_io.schemas'],
    install_requires=['mdf_toolbox>=0.4.2', 'stevedore>=1.28.0'],
    extras_require={
        'electron_microscopy': ['hyperspy>=1.4.1'],
        'image': ['Pillow>=5.1.0'],
        'file': ['python-magic>=0.4.15'],
        'crystal_structure': ['pymatgen>=2018.11.30', 'ase>=3'],
        'dft': ['dfttopif>=1.1.0'],
        'ase': ['ase>=3']
    },
    include_package_data=True,
    package_data={'materials_io.schemas': ['*.json']},
    entry_points={
        'materialsio.parser': [
            'generic = materials_io.file:GenericFileParser',
            'em = materials_io.electron_microscopy:ElectronMicroscopyParser',
            'image = materials_io.image:ImageParser',
            'crystal = materials_io.crystal_structure:CrystalStructureParser',
            'dft = materials_io.dft:DFTParser',
            'ase = materials_io.ase:AseParser'
        ]
    }
)
