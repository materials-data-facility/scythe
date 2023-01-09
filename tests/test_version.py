from scythe import version


def test_version():
    assert version.__version__ == '0.1.1'
