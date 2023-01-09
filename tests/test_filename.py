import os

import pytest

from scythe.filename import FilenameExtractor


@pytest.fixture
def test_files():
    # These are not files on disk, because no data is read from the files directly
    return ["He_abcdeffoo:FOO.txt",
            "Al123Smith_et_al.and_co.data",
            os.path.join(os.path.dirname(__file__), 'data', 'filename', "O2foo:bar")]


@pytest.fixture
def extractor():
    return FilenameExtractor()


@pytest.fixture
def mappings():
    return [{
        "material.composition": "^.{2}",  # First two chars are always composition
        "custom.foo": "foo:.{3}",  # 3 chars after foo is value of foo
        "custom.ext": "\\..{3,4}$"  # 3 or 4 char extension
    }]


def test_filename(extractor, test_files, mappings):
    # Run test extractions
    outputs = [{
        'custom': {
            'ext': '.txt',
            'foo': 'foo:FOO'
        },
        'material': {
            'composition': 'He'
        }
    }, {
        'custom': {
            'ext': '.data'
        },
        'material': {
            'composition': 'Al'
        }
    }, {
        'custom': {
            'foo': 'foo:bar'
        },
        'material': {
            'composition': 'O2'
        }
    }]

    assert extractor.extract(test_files[0], context={"mapping": mappings[0]}) == outputs[0]
    assert extractor.extract(test_files[1], context={"mapping": mappings[0]}) == outputs[1]
    assert extractor.extract(test_files[2], context={"mapping": mappings[0]}) == outputs[2]

    # Test failure modes
    # No mapping provided
    with pytest.raises(Exception):
        extractor.extract(test_files[0])
