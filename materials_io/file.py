from materials_io.base import BaseSingleFileParser
from hashlib import sha512
import magic
import json
import os


class GenericFileParser(BaseSingleFileParser):
    """Gathers basic file information"""

    def __init__(self, store_path=False, compute_hash=True):
        """
        Args:
            store_path (bool): Whether to record the path of the file
            compute_hash (bool): Whether to compute the hash of a file
        """
        super().__init__()
        self.store_path = store_path
        self.compute_hash = compute_hash

    def _parse_file(self, path, context=None):
        output = {
            "mime_type": magic.from_file(path, mime=True),
            "length": os.path.getsize(path),
            "filename": os.path.basename(path),
        }
        if self.store_path:
            output['path'] = path
        if self.compute_hash:
            sha = sha512()
            with open(path, 'rb') as fp:
                while True:
                    data = fp.read(65536)
                    if not data:
                        break
                    sha.update(data)
            output['hash'] = sha.hexdigest()
        return output

    def implementors(self):
        return ['Logan Ward']

    def version(self):
        return '0.0.1'

    @property
    def schema(self):
        with open(os.path.join(os.path.dirname(__file__), 'schemas', 'file.json')) as fp:
            return json.load(fp)
