from typing import List, Iterator, Tuple, Iterable, Union, Sequence
from abc import ABC, abstractmethod
import logging
import os

from scythe.utils.grouping import preprocess_paths

logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """Abstract base class for a metadata extractor

    This class defines the interface for all extractors in Scythe. Each new extractor must
    implement the :meth:`parse`, :meth:`version`, and :meth:`implementors` functions. The
    :meth:`group` method should be overridden to generate smart groups of file (e.g., associating
    the inputs and outputs to the same calculation) :meth:`citations` can be used if there
    are papers that should be cited if the extractor is used as part of a scientific publication.

    See the `Scythe Contributor Guide <contributor-guide.html>`_ for further details.
    """

    def identify_files(self, path: str, context: dict = None) -> \
            Iterator[Tuple[str]]:
        """Identify all groups of files likely to be compatible with this extractor

        Uses the :meth:`group` function to determine groups of files that should be parsed together.

        Args:
            path (str): Root of directory to group together
            context (dict): Context about the files
        Yields:
            ([str]) Groups of eligible files
        """

        # Walk through the directories
        for root, dirs, files in os.walk(path):
            # Generate the full paths
            dirs = [os.path.join(root, d) for d in dirs]
            files = [os.path.join(root, f) for f in files]

            # Get any groups from this directory
            for group in self.group(files, dirs, context):
                yield group

    def extract_directory(self, path: str, context: dict = None) -> \
            Iterator[Tuple[Tuple[str], dict]]:
        """Run extractor on all appropriate files in a directory

        Skips files that throw exceptions while parsing

        Args:
            path (str): Root of directory to extract metadata from
            context (dict): Context about the files
        Yields:
            ([str], dict): Tuple of the group identity and the metadata unit
        """

        for group in self.identify_files(path, context):
            try:
                metadata_unit = self.extract(group, context)
            except Exception:
                continue
            else:
                yield group, metadata_unit

    @abstractmethod
    def extract(self, group: Iterable[str], context: dict = None) -> dict:
        """Extract metadata from a group of files

        A group of files is a set of 1 or more files that describe the same object
        and will be used together to create a single metadata record.

        Arguments:
            group ([str]):  A list of one or more files that should be parsed together
            context (dict): Context about the files

        Returns:
            (dict): The parsed results, in JSON-serializable format.
        """

    def group(self, files: Union[str, List[str]], directories: List[str] = None,
              context: dict = None) -> Iterator[Tuple[str, ...]]:
        """Identify a groups of files and directories that should be parsed together

        Will create groups using only the files and directories included as input.

        The files of files are _all_ files that could be read by this extractor,
        which may include many false positives.

        Args:
            files (str or [str]): List of files to consider grouping
            directories ([str]): Any directories to consider group as well
            context (dict): Context about the files
        Yields:
            ((str)): Groups of files
        """

        # Make sure file paths are strings or Path-like objects
        files = preprocess_paths(files)

        # Default: Every file is in its own group
        for f in files:
            yield f,

    def citations(self) -> List[str]:
        """Citation(s) and reference(s) for this extractor

        Returns:
            ([str]): each element should be a string citation in BibTeX format
        """
        return []

    @abstractmethod
    def implementors(self) -> List[str]:
        """List of implementors of the extractor

        These people are the points-of-contact for addressing errors or modifying the extractor

        Returns:
            ([str]): List of implementors in the form "FirstName LastName <email@provider>"
        """

    @abstractmethod
    def version(self) -> str:
        """Return the version of the extractor

        Returns:
            (str): Version of the extractor
        """

    @property
    def schema(self) -> dict:
        """Schema for the output of the extractor"""
        return {
            "$schema": "http://json-schema.org/schema#"
        }


class BaseSingleFileExtractor(BaseExtractor):
    """Base class for extractors that only ever considers a single file at a time

    Instead of implementing :meth:`parse`, implement :meth:`_parse_file`"""

    @abstractmethod
    def _extract_file(self, path: str, context=None):
        """Generate the metadata for a single file

        Args:
            path (str): Path to the file
            context (dict): Optional context information about the file
        Returns:
            (dict): Metadata for the file
        """

    def extract(self, group: Union[str, Sequence[str]], context=None):
        # Error catching: allows for single files to passed not as list
        if isinstance(group, str):
            return self._extract_file(group, context)

        # Assumes that the group must have exactly one file
        if len(group) > 1:
            raise ValueError('Extractor only takes a single file at a time')

        return self._extract_file(group[0], context)
