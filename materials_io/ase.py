import json
from ase.io import read, write
from io import StringIO

from materials_io.base import BaseSingleFileParser


class AseParser(BaseSingleFileParser):
    """Parse information from atomistic simulation input files using ASE.

       ASE can read many file types. These can be found at
       https://wiki.fysik.dtu.dk/ase/ase/io/io.html

       Metadata are generated as ASE JSON DB format
       https://wiki.fysik.dtu.dk/ase/ase/db/db.html
    """

    def _parse_file(self, path, context=None):
        # Attempt to read the file with ASE
        # To return ASE JSON DB requires writing to file.
        # Here we use StringIO instead of a file on disk.

        record = {}
        fobj = StringIO()
        m = read(path)
        write(images=m, format="json", filename=fobj)
        js = json.loads(fobj.getvalue())

        # Select the first record.
        # TODO: Test this against multiple records
        record = js['1']
        record['chemical_formula'] = m.get_chemical_formula()
        return record

    def implementors(self):
        return ['Ben Blaiszik <blaiszik@uchicago.edu>']

    def version(self):
        return '0.0.1'
