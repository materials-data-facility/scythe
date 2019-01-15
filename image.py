from base import BaseParser
from PIL import Image


class ParseImage(BaseParser):
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
