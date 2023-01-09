import os

import pytest

from scythe.xml import XMLExtractor


@pytest.fixture
def test_files():
    return [os.path.join(os.path.dirname(__file__), 'data', 'xml', 'test_xml.xml')]


@pytest.fixture
def fail_file():
    return os.path.join(os.path.dirname(__file__), 'data', 'fail_file.dat')


@pytest.fixture
def extractor():
    return XMLExtractor()


@pytest.fixture
def mappings():
    return [{
        "custom": {
            "foo": "root.dict1.field1",
            "bar": "root.dict2.nested1.field1",
            "missing": "root.na_val"
        },
        "material": {
            "composition": "root.compost"
        }
    }, {
        "custom.foo": "root.dict1.field1",
        "custom.bar": "root.dict2.nested1.field1",
        "custom.missing": "root.na_val",
        "material.composition": "root.compost"
    }]


def test_xml(extractor, test_files, fail_file, mappings):
    # Run test extractions
    output_na_unset = {
        "material": {
            "composition": "CN25"
        },
        "custom": {
            "foo": "value1",
            "bar": "baz",
            "missing": "na"
        }
    }
    output_na_set = {
        "material": {
            "composition": "CN25"
        },
        "custom": {
            "foo": "value1",
            "bar": "baz"
        }
    }

    assert extractor.extract(test_files[0], context={"mapping": mappings[0]}) == output_na_unset
    assert extractor.extract(test_files[0], context={"mapping": mappings[1]}) == output_na_unset
    assert extractor.extract(test_files[0], context={"mapping": mappings[0],
                                                   "na_values": ["na"]}) == output_na_set
    assert extractor.extract(test_files[0], context={"mapping": mappings[1],
                                                   "na_values": "na"}) == output_na_set

    # Test failure modes
    with pytest.raises(Exception):
        extractor.extract(fail_file)
    # No mapping provided
    with pytest.raises(Exception):
        extractor.extract(test_files[0])
