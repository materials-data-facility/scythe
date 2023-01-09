from PIL import Image

from scythe.base import BaseSingleFileParser


class ImageParser(BaseSingleFileParser):
    """Retrieves basic information about an image"""

    def _parse_file(self, file_path, context=None):
        im = Image.open(file_path)
        return {
            "image": {
                "width": im.width,
                "height": im.height,
                "format": im.format,
                "megapixels": (im.width * im.height) / 1000000,
                "shape": [
                    im.height,
                    im.width,
                    len(im.getbands())
                ]
            }
        }

    def implementors(self):
        return ['Jonathon Gaff']

    def version(self):
        return '0.0.2'
