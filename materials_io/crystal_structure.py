from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.core import Structure
from mdf_toolbox import dict_merge
from ase.io import read

from materials_io.base import BaseParser


class ParseCrystalStructure(BaseParser):
    """Parse information about a crystal structure"""

    def parse(self, group, context=None):
        record = {}

        for data_file in group:
            material = {}
            crystal_structure = {}
            # Attempt to read the file
            try:
                # Read with ASE
                ase_res = read(data_file)
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
                    pmg_s = Structure.from_file(data_file)
                except Exception:
                    # Can't read file
                    continue

            # Parse material block
            material["composition"] = pmg_s.formula.replace(" ", "")

            # Parse crystal_structure block
            crystal_structure["space_group_number"] = pmg_s.get_space_group_info()[1]
            crystal_structure["number_of_atoms"] = float(pmg_s.composition.num_atoms)
            crystal_structure["volume"] = float(pmg_s.volume)
            crystal_structure["stoichiometry"] = pmg_s.composition.anonymized_formula

            # Add to record
            record = dict_merge(record, {"material": material,
                                         "crystal_structure": crystal_structure})
        return record

    def implementors(self):
        return ['Jonathon Gaff']
