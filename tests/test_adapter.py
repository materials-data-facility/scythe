from materials_io.adapters.base import NOOPAdapter
from materials_io.testing import NOOPParser


def test_compatibility():
    adapter = NOOPAdapter()
    parser = NOOPParser()

    # Make sure `None` is always compatible
    assert adapter.version() is None
    assert adapter.check_compatibility(parser)

    # Make sure giving the adapter the same version number works
    adapter.version = lambda: parser.version()
    assert adapter.check_compatibility(parser)

    # Make sure giving it a different version number breaks compatibility
    adapter.version = lambda: parser.version() + '1'
    assert not adapter.check_compatibility(parser)
