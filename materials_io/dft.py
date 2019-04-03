from typing import Union, Iterable, Tuple
from materials_io.base import BaseParser
from dfttopif import files_to_pif
from operator import itemgetter
from glob import glob
import itertools
import os


# List of files that are known to the VASP parser
_vasp_file_names = ["outcar", "incar", "chgcar", "wavecar", "wavcar",
                    "oszicar", "ibzcar", "kpoints", "doscar", "poscar",
                    "contcar", "vasp_run.xml", "xdatcar"]


class DFTParser(BaseParser):
    """Extract data from Density Functional Theory calculation results

    Uses the `dfttopif <https://github.com/CitrineInformatics/pif-dft>`_ parser to extract
    metadata from each file
    """

    def __init__(self, quality_report=False):
        """Initialize a featurizer

        Args:
            quality_report (bool): Whether to generate a quality report
        """
        self.quality_report = quality_report

    def group(self, paths: Union[str, Iterable[str]], context: dict = None):
        # Check arguments
        if isinstance(paths, (str,)):
            paths = [paths]

        # Clean paths
        paths = [os.path.abspath(os.path.expanduser(f)) for f in paths]

        # Find all of the files, and attempt to group them
        files = filter(os.path.isfile, paths)
        for group in self._group_vasp(files):
            yield group

        # Recurse into directories
        for path in filter(os.path.isdir, paths):
            for group in self.group(glob(os.path.join(path, '*'))):
                yield group

    def _group_vasp(self, files: Iterable[str]) -> Iterable[Tuple[str, ...]]:
        """Find groupings of files associated with VASP calculations

        Finds files that start with the name "OUTCAR" (not case sensitive) and groups
        those files together with any file that share the same postfix
        (e.g., "OUTCAR.1" and "INCAR.1" are grouped together)

        Args:
            files ([str]): List of files to be grouped
        Yields:
            ((files]): List of VASP files from the same calculation
        """

        # Get the files that are likely VASP files, which we define as
        #  those which start with the name of a known vasp file.
        vasplike_files = []  # List of (path, type, postfix)
        for file in files:
            # TODO (lw): This logic is likely useful elsewhere
            # Find if the filename matches a known type
            name = os.path.basename(file)
            name_lower = name.lower()
            matches = [name_lower.startswith(n) for n in _vasp_file_names]
            if not any(matches):
                continue

            # Get the extension of the file
            match_id = matches.index(True)
            vtype = _vasp_file_names[match_id]
            ext = name[len(vtype):]

            # Add to the list
            vasplike_files.append((file, vtype, ext))

        # Group files by postfix type
        sort_key = itemgetter(2)
        for k, group in itertools.groupby(sorted(vasplike_files, key=sort_key),
                                          key=sort_key):
            yield [x[0] for x in group]

    def parse(self, group: Iterable[str], context: dict = None):
        return files_to_pif(group, quality_report=self.quality_report).as_dictionary()

    def implementors(self):
        return ['Logan Ward']

    def version(self):
        return '0.0.1'
