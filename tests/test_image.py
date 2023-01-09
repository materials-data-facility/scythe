import pytest
import os

from scythe.image import ImageExtractor


@pytest.fixture
def test_image():
    return os.path.join(os.path.dirname(__file__), 'data', 'image', 'dog2.jpeg')


def test_parse(test_image):
    p = ImageExtractor()
    assert (p.extract([test_image]) == {'image': {'format': 'JPEG', 'height': 1000,
                                                'megapixels': 1.91, 'width': 1910,
                                                'shape': [1000, 1910, 3]}})
