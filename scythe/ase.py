import json
import datetime
from ase.io.jsonio import create_ndarray
from ase.io import read, write
from io import StringIO
import numpy as np

from scythe.base import BaseSingleFileExtractor


def object_hook(dct):
    """Custom decoder for ASE JSON objects

    Does everything *except* reconstitute the JSON object and
    also converts numpy arrays to lists

    Adapted from ase.io.jsonio

    Args:
        dct (dict): Dictionary to reconstitute to an ASE object
    """
    if '__datetime__' in dct:
        return datetime.datetime.strptime(dct['__datetime__'], '%Y-%m-%dT%H:%M:%S.%f')

    if '__complex__' in dct:
        return complex(*dct['__complex__'])

    if '__ndarray__' in dct:
        return create_ndarray(*dct['__ndarray__'])

    # No longer used (only here for backwards compatibility):
    if '__complex_ndarray__' in dct:
        r, i = (np.array(x) for x in dct['__complex_ndarray__'])
        return r + i * 1j

    return dct


class ASEExtractor(BaseSingleFileExtractor):
    """Parse information from atomistic simulation input files using ASE.

    ASE can read many file types. These can be found at https://wiki.fysik.dtu.dk/ase/ase/io/io.html

    Metadata are generated as ASE JSON DB format: https://wiki.fysik.dtu.dk/ase/ase/db/db.html
    """

    def _extract_file(self, path, context=None):
        # Attempt to read the file with ASE
        # To return ASE JSON DB requires writing to file.
        # Here we use StringIO instead of a file on disk.

        fobj = StringIO()
        m = read(path)
        write(images=m, format="json", filename=fobj)
        js = json.loads(fobj.getvalue(), object_hook=object_hook)

        # Select the first record.
        # TODO: Test this against multiple records
        record = js['1']
        record['chemical_formula'] = m.get_chemical_formula()
        return record

    def implementors(self):
        return ['Ben Blaiszik <blaiszik@uchicago.edu>']

    def version(self):
        return '0.0.1'
