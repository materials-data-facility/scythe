import tomli
import pathlib
# single source of truth for package version,
# see https://packaging.python.org/en/latest/single_source_version/

with open(pathlib.Path(__file__).parent / '..' / 'pyproject.toml', 'rb') as f:
    toml_dict = tomli.load(f)

__version__ = toml_dict["tool"]["poetry"]["version"]
