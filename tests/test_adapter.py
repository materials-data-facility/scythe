from materials_io.adapters.base import NOOPAdapter, GreedySerializeAdapter
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


def test_greedy_adapter_unserializable():
    adapter = GreedySerializeAdapter()
    unserializable_bytes = {'key': b'\x03\xdd'}
    s = adapter.transform(unserializable_bytes)
    assert s == '{"key": "<<Unserializable type: bytes>>"}'
