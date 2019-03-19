from setuptools import setup, find_packages
import os

# single source of truth for package version
version_ns = {}
with open(os.path.join("materials_io", "version.py")) as f:
    exec(f.read(), version_ns)
version = version_ns['__version__']

setup(
    name="materials_io.rst",
    packages=find_packages(include=['materials_io']),
    install_requires=["Pillow>=5.1.0"],
    version=version
)
