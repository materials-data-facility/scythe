import pytest
from materials_io.image import ParseImage

def test_ParseImage():
	path = "data/image/dog2.jpeg"
	p = ParseImage()
	assert (p.parse([path]) == [{'image': {'format': 'JPEG',
  	'height': 1000,
  	'megapixels': 1.91,
  	'width': 1910}}])