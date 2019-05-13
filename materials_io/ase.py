import json
import ase
from io import StringIO

from materials_io.base import BaseSingleFileParser

class AseParser(BaseSingleFileParser):
    """Parse information from an input file using ASE.

       ASE can read many file types. These can be found at 
       https://wiki.fysik.dtu.dk/ase/ase/io/io.html

       Metadata are generated as ASE JSON DB format
       https://wiki.fysik.dtu.dk/ase/ase/db/db.html
    
    """

    def _parse_file(self, path, context=None):
        record = {}
        # Attempt to read the file with ASE
        try: 
            fobj = StringIO() 
            m = ase.io.read(path)
            ase.io.write(images=m, format="json", filename=fobj)
            js = json.loads(fobj.getvalue())
            record = js['1']
            record['chemical_formula'] = m.get_chemical_formula()
            record['']
        except:
             raise ValueError('File not readable by ase: {}'.format(path))
        
        return record
    
    def implementors(self):
        return ['Ben Blaiszik <blaiszik@uchicago.edu>']
    
    def version(self):
        return '0.0.1'