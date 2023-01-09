from scythe.file import GenericFileParser
import pytest
import os


def test_file():
    my_file = os.path.join(os.path.dirname(__file__), 'data', 'image', 'dog2.jpeg')
    parser = GenericFileParser(store_path=True, compute_hash=True)
    output = parser.parse([my_file])
    expected = {
        'mime_type': 'image/jpeg',
        'length': 269360,
        'filename': 'dog2.jpeg',
        'path': my_file,
        'data_type': 'JPEG image data, JFIF standard 1.01, resolution (DPI), '
                     'density 300x300, segment length 16, Exif Standard: [TIFF '
                     'image data, little-endian, direntries=2, GPS-Data], '
                     'baseline, precision 8, 1910x1000, frames 3',
        'sha512': '1f47ed450ad23e92caf1a0e5307e2af9b13edcd7735ac9685c9f21c'
                  '9faec62cb95892e890a73480b06189ed5b842d8b265c5e47cc6cf27'
                  '9d281270211cff8f90'}

    # be defensive against data_type, which will only be present if the user has libmagic installed
    if 'data_type' not in output:
        del expected['data_type']
        del expected['mime_type']
        assert output == expected
        assert isinstance(parser.schema, dict)
        pytest.xfail("'data_type' was not present in the parser output, most likely because "
                     "libmagic is not properly installed")

    for i in ['JPEG image data', 'density 300x300', 'TIFF image data',
              '1910x1000']:
        assert i in output['data_type']
    del output['data_type']
    del expected['data_type']
    assert output == expected
    assert isinstance(parser.schema, dict)
