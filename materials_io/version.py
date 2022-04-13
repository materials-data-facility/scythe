try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    # for Python <3.8 add 'importlib_metadata' as a dependency
    import importlib_metadata  # type: ignore

# single source of truth for package version,
# see https://packaging.python.org/en/latest/single_source_version/

__version__ = importlib_metadata.version('materials_io')
