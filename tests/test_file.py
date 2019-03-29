from materials_io.file import GenericFileParser
import os


def test_file():
    my_file = os.path.join(os.path.dirname(__file__), 'data', 'image', 'dog2.jpeg')
    parser = GenericFileParser(store_path=True, compute_hash=True)
    assert parser.parse([my_file]) == {
        'mime_type': 'image/jpeg', 'length': 269360, 'filename': 'dog2.jpeg',
        'path': my_file,
        'hash': '1f47ed450ad23e92caf1a0e5307e2af9b13edcd7735ac9685c9f21c9faec62'
                'cb95892e890a73480b06189ed5b842d8b265c5e47cc6cf279d281270211cff8f90'}
    assert isinstance(parser.schema, dict)
