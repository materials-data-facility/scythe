from base import BaseParser
from PIL import Image  # noqa: E402

class ParseImage(BaseParser):
    def parse(self, group, context=None):
        record = {}
        try:
            im = Image.open(group[0])
            record={
                "image": {
                    "width": im.width,
                    "height": im.height,
                    "format": im.format
                }
            }
        except Exception:
            pass
        return record