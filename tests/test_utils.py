from materials_io.utils.interface import get_available_parsers, execute_parser, run_all_parsers
from materials_io.image import ImageParser
import os


cwd = os.path.dirname(__file__)


def test_list_parsers():
    assert 'image' in get_available_parsers()


def test_execute_parser():
    image = os.path.join(cwd, 'data', 'image', 'dog2.jpeg')
    assert ImageParser().parse([image]) == execute_parser('image', [image])


def test_run_all_parsers():
    path = os.path.join(cwd, 'data', 'image')
    output = list(run_all_parsers(path))
    assert len(output) > 0
    assert len(output[0]) == 3
    assert isinstance(output[0][0], tuple)
    assert isinstance(output[0][1], str)
    assert isinstance(output[0][2], dict)
