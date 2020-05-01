import os
from setuptools import setup, find_packages

# single source of truth for package version
version_ns = {}
with open(os.path.join("materials_io", "version.py")) as f:
    exec(f.read(), version_ns)
version = version_ns['__version__']

# Requirements for the extras
extra_reqs = {
    'ase': ['ase>=3.19'],
    'crystal_structure': ['pymatgen>=2018.11.30', 'ase>=3'],
    'csv': ['tableschema>=1<2'],
    'dft': ['dfttopif>=1.1.0'],
    'electron_microscopy': ['hyperspy>=1.4.1'],
    'file': ['python-magic>=0.4.15'],
    'image': ['Pillow>=5.1.0'],
    'xml': ['xmltodict>=0.12.0']
}
extra_reqs['all'] = set(sum(extra_reqs.values(), []))

setup(
    name="materials_io",
    version=version,
    packages=find_packages(include=['materials_io*']) + ['materials_io.schemas'],
    install_requires=['mdf_toolbox>=0.5.3', 'stevedore>=1.28.0', 'materials_io'],
    extras_require=extra_reqs,
    include_package_data=True,
    package_data={'materials_io.schemas': ['*.json']},
    entry_points={
        'materialsio.parser': [
            'ase = materials_io.ase:AseParser',
            'crystal = materials_io.crystal_structure:CrystalStructureParser',
            'csv = materials_io.csv:CSVParser'
            'dft = materials_io.dft:DFTParser',
            'em = materials_io.electron_microscopy:ElectronMicroscopyParser',
            'filename = materials_io.filename:FilenameExtractor',
            'generic = materials_io.file:GenericFileParser',
            'image = materials_io.image:ImageParser',
            'json = materials_io.json:JSONExtractor',
            'noop = materials_io.testing:NOOPParser',
            'tdb = materials_io.tdb:TDBExtractor',
            'xml = materials_io.xml:XMLExtractor',
            'yaml = materials_io.yaml:YAMLExtractor'
        ],
        'materialsio.adapter': [
            'noop = materials_io.adapters.base:NOOPAdapter',
            'serialize = materials_io.adapters.base:SerializeAdapter'
        ]
    }
)
