from materials_io.utils import get_available_parsers, execute_parser
from materials_io.image import ImageParser
import os


def test_list_parsers():
    assert 'image' in get_available_parsers()


def test_execute_parser():
    image = os.path.join(os.path.dirname(__file__), 'data', 'image', 'dog2.jpeg')
    assert ImageParser().parse([image]) == execute_parser('image', [image])
