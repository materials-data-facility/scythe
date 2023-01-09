from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.core import Structure
from ase.io import read

from scythe.base import BaseSingleFileExtractor


class CrystalStructureExtractor(BaseSingleFileExtractor):
    """Extract information about a crystal structure from many types of files.

     Uses either ASE or Pymatgen on the back end"""

    def _extract_file(self, path, context=None):
        material = {}
        crystal_structure = {}
        # Attempt to read the file
        try:
            # Read with ASE
            ase_res = read(path)
            # Check data read, validate crystal structure
            if not ase_res or not all(ase_res.get_pbc()):
                raise ValueError("No valid data")
            else:
                # Convert ASE Atoms to Pymatgen Structure
                pmg_s = AseAtomsAdaptor.get_structure(ase_res)
        # ASE failed to read file
        except Exception:
            try:
                # Read with Pymatgen
                pmg_s = Structure.from_file(path)
            except Exception:
                # Can't read file
                raise ValueError('File not readable by pymatgen or ase: {}'.format(path))

        # Parse material block
        material["composition"] = pmg_s.formula.replace(" ", "")

        # Parse crystal_structure block
        crystal_structure["space_group_number"] = pmg_s.get_space_group_info()[1]
        crystal_structure["number_of_atoms"] = float(pmg_s.composition.num_atoms)
        crystal_structure["volume"] = float(pmg_s.volume)
        crystal_structure["stoichiometry"] = pmg_s.composition.anonymized_formula

        record = {}
        if material:
            record["material"] = material
        if crystal_structure:
            record["crystal_structure"] = crystal_structure
        return record

    def implementors(self):
        return ['Jonathon Gaff']

    def version(self):
        return '0.0.1'
