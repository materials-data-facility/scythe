from typing import Union, Iterable, Tuple, List
from scythe.utils.grouping import preprocess_paths, group_by_postfix
from scythe.base import BaseExtractor
from dfttopif import files_to_pif
from operator import itemgetter
import itertools
import os


# List of files that are known to the VASP parser
_vasp_file_names = ["outcar", "incar", "chgcar", "wavecar", "wavcar", "oszicar", "ibzcar",
                    "kpoints", "doscar", "poscar", "contcar", "vasp_run.xml", "xdatcar"]


class DFTExtractor(BaseExtractor):
    """Extract metadata from Density Functional Theory calculation results

    Uses the `dfttopif <https://github.com/CitrineInformatics/pif-dft>`_ parser to extract metadata from each file
    """

    def __init__(self, quality_report=False):
        """Initialize the extractor

        Args:
            quality_report (bool): Whether to generate a quality report
        """
        self.quality_report = quality_report

    def group(self, files: Union[str, List[str]], directories: List[str] = None,
              context: dict = None):
        # Convert paths into standardized form
        files = set(preprocess_paths(files))

        # Find all files, and attempt to group them
        for group in self._group_vasp(files):  # VASP grouping logic
            # Remove all files matched as VASP from the matchable files
            files.difference_update(group)
            yield group
        for group in self._group_pwscf(files):
            yield group  # Do not remove, as the PWSCF group is not reliable

    def _group_vasp(self, files: Iterable[str]) -> Iterable[Tuple[str, ...]]:
        """Find groupings of files associated with VASP calculations

        Find files that start with the name "OUTCAR" (not case sensitive) and groups those files
        together with any file that share the same postfix (e.g., "OUTCAR.1" and "INCAR.1" are
        grouped together)

        Args:
            files ([str]): List of files to be grouped
        Yields:
            ((files)): List of VASP files from the same calculation
        """

        for group in group_by_postfix(files, _vasp_file_names):
            yield group

    def _group_pwscf(self, files: Iterable[str]) -> Iterable[Tuple[str, ...]]:
        """Assemble groups of files that are potentially PWSCF calculations

        Args:
            files ([str]): List of files to be grouped
        Yields:
            ((str)): Groups of potential-pwscf files
        """

        # For now, we just group files by directory
        #  TODO (lw): Find files that have PWSCF flags in them
        #  TODO (lw): Read PWSCF input files to know the save directory
        file_and_dir = [(os.path.dirname(f), f) for f in files]
        for k, group in itertools.groupby(sorted(file_and_dir), key=itemgetter(0)):
            yield [x[1] for x in group]

    def extract(self, group: Iterable[str], context: dict = None):
        return files_to_pif(group, quality_report=self.quality_report).as_dictionary()

    def implementors(self):
        return ['Logan Ward <lward@anl.gov>']

    def version(self):
        return '0.0.1'
