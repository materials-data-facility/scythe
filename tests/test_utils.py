from scythe.utils.interface import (get_available_parsers, execute_parser,
                                    get_available_adapters, run_all_parsers_on_directory,
                                    ParseResult)
from scythe.utils import set_nested_dict_value
from scythe.image import ImageParser
import pytest
import json
import os


cwd = os.path.dirname(__file__)


def test_list_parsers():
    assert 'image' in get_available_parsers()


def test_execute_parser():
    image = os.path.join(cwd, 'data', 'image', 'dog2.jpeg')
    assert ImageParser().parse([image]) == execute_parser('image', [image])
    assert execute_parser('image', [image], adapter='noop') == execute_parser('image', [image])


def test_run_all_parsers():
    path = os.path.join(cwd, 'data', 'image')
    output = list(run_all_parsers_on_directory(path))
    assert len(output) > 0
    assert len(output[0]) == 3
    assert isinstance(output[0][0], tuple)
    assert isinstance(output[0][1], str)
    assert isinstance(output[0][2], dict)

    # Re-run parsers with adapters
    output_noop = list(run_all_parsers_on_directory(path, default_adapter='noop'))
    assert output == output_noop
    output_json = list(run_all_parsers_on_directory(path, default_adapter='serialize'))
    assert output == [ParseResult(x.group, x.parser, json.loads(x.metadata)) for x in output_json]

    # Test the matching
    output_matching = list(run_all_parsers_on_directory(path, adapter_map={'file': 'serialize'}))
    assert all(isinstance(x.metadata, str if x.parser == 'file' else dict)
               for x in output_matching)
    output_matching = list(run_all_parsers_on_directory(path, adapter_map={'file': 'noop'},
                                                        default_adapter='serialize'))
    assert all(isinstance(x.metadata, str if x.parser != 'file' else dict)
               for x in output_matching)

    # This matching test fails if we have other packages with adapters on the system
    adapters = set(get_available_adapters().keys())
    if adapters == {'noop', 'serialize'}:
        output_matching = list(run_all_parsers_on_directory(path, adapter_map='match',
                                                            default_adapter='serialize'))
        assert all(isinstance(x.metadata, str if x.parser != 'noop' else dict)
                   for x in output_matching)

    # Test the error case
    with pytest.raises(ValueError):
        list(run_all_parsers_on_directory(path, adapter_map='matching',
                                          default_adapter='serialize'))

    # Test specifying parsers
    assert set([x.parser for x in output]).issuperset(['image', 'generic'])
    output_limit = list(run_all_parsers_on_directory(path, exclude_parsers=['image']))
    assert 'image' not in [x.parser for x in output_limit]
    output_limit = list(run_all_parsers_on_directory(path, include_parsers=['image']))
    assert set([x.parser for x in output_limit]) == {'image'}
    with pytest.raises(ValueError):
        list(run_all_parsers_on_directory(path, include_parsers=['image'],
                                          exclude_parsers=['image']))
    with pytest.raises(ValueError):
        list(run_all_parsers_on_directory(path, include_parsers=['totally-not-a-parser']))


def test_list_adapters():
    assert 'noop' in get_available_adapters()


def test_set_nested_dict():
    dest_dict1 = {
        'key1': 'val1',
        'key2': {
            'key2.1': 'val2.1',
            'key2.2': 'val2.2'}
    }
    dest_dict2 = {
        'key1': 'val1',
        'key2': {
            'key2.1': 'val2.1',
            'key2.2': 'val2.2'}
    }

    set_nested_dict_value(dest_dict2, ('key3', 'key3.1'), None)
    assert dest_dict1 == dest_dict2

    set_nested_dict_value(dest_dict2, ('key3', 'key3.1'), 4)
    assert dest_dict2 == {
        'key1': 'val1',
        'key2': {
            'key2.1': 'val2.1',
            'key2.2': 'val2.2'},
        'key3': {'key3.1': 4}
    }

    set_nested_dict_value(dest_dict2, ('key3', 'key3.1'), 5, override=False)
    assert dest_dict2 == {
            'key1': 'val1',
            'key2': {
                'key2.1': 'val2.1',
                'key2.2': 'val2.2'},
            'key3': {'key3.1': 4}
    }

    set_nested_dict_value(dest_dict2, ('key3', 'key3.1'), 5, override=True)
    assert dest_dict2 == {
        'key1': 'val1',
        'key2': {
            'key2.1': 'val2.1',
            'key2.2': 'val2.2'},
        'key3': {'key3.1': 5}
    }
