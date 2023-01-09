from scythe.base import BaseSingleFileExtractor
from hashlib import sha512
from warnings import warn
import json
import os


try:
    import magic
except ImportError as e:
    if 'failed to find libmagic' in str(e):
        warn('The libmagic library is not installed. '
             'See: https://github.com/ahupp/python-magic#installation')
    else:
        warn('The python wrapper for libmagic is not installed. '
             'If desired, call: https://github.com/ahupp/python-magic#installation')
    magic = None


class GenericFileExtractor(BaseSingleFileExtractor):
    """Gather basic file information"""

    def __init__(self, store_path=True, compute_hash=True):
        """
        Args:
            store_path (bool): Whether to record the path of the file
            compute_hash (bool): Whether to compute the hash of a file
        """
        super().__init__()
        self.store_path = store_path
        self.compute_hash = compute_hash

    def _extract_file(self, path, context=None):
        output = {
            "length": os.path.getsize(path),
            "filename": os.path.basename(path),
        }

        # If magic imported properly, use it
        if magic is not None:
            output["mime_type"] = magic.from_file(path, mime=True)
            output["data_type"] = magic.from_file(path)

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
            output['sha512'] = sha.hexdigest()
        return output

    def implementors(self):
        return ['Logan Ward']

    def version(self):
        return '0.0.1'

    @property
    def schema(self):
        with open(os.path.join(os.path.dirname(__file__), 'schemas', 'file.json')) as fp:
            return json.load(fp)
