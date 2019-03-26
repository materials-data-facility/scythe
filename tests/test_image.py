import pytest
import os

from materials_io.image import ImageParser


@pytest.fixture
def test_image():
    return os.path.join(os.path.dirname(__file__), 'data', 'image', 'dog2.jpeg')


def test_parse(test_image):
    p = ImageParser()
    assert (p.parse([test_image]) == {'image': {'format': 'JPEG', 'height': 1000,
                                                'megapixels': 1.91, 'width': 1910}})
