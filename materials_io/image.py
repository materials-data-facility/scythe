from PIL import Image

from materials_io.base import BaseParser


class ParseImage(BaseParser):
    """Retrieves basic information about an image"""

    def parse(self, group, context=None):
        records = []
        for file_path in group:
            try:
                im = Image.open(file_path)
                records.append({
                    "image": {
                        "width": im.width,
                        "height": im.height,
                        "format": im.format,
                        "megapixels": (im.width * im.height) / 1000000
                    }
                })
            except Exception:
                pass
        return records

    def implementors(self):
        return ['Jonathon Gaff']
