import os
# pycalphad and hyperspy imports require this env var set
# Triggers E402: module level import not at top of file, so noqa set for other imports
os.environ["MPLBACKEND"] = "agg"
import pycalphad  # noqa: E402

from scythe.base import BaseSingleFileExtractor  # noqa: E402


class TDBExtractor(BaseSingleFileExtractor):
    """Extract metadata from a Thermodynamic Database (TBD) file.

    Built atop `PyCALPHAD <https://pycalphad.org/docs/latest/>`_.
    """

    def _extract_file(self, path, context=None):
        material = {}
        calphad = {}
        # Attempt to read the file
        calphad_db = pycalphad.Database(path)
        composition = ""
        for element in calphad_db.elements:
            if element.isalnum():
                element = element.lower()
                element = element[0].upper() + element[1:]
                composition += element

        phases = list(calphad_db.phases.keys())

        if composition:
            material['composition'] = composition
        if phases:
            calphad['phases'] = phases

        # Create record
        record = {}
        if material:
            record["material"] = material
        if calphad:
            record["calphad"] = calphad
        return record

    def implementors(self):
        return ['Jonathon Gaff']

    def version(self):
        return '0.0.1'
