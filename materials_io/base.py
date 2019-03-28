from typing import List, Iterator, Tuple, Iterable
from abc import ABC, abstractmethod
from mdf_toolbox import dict_merge
import logging
import os

logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """Abstract base class for a file parser

    This class defines the interface for all parsers in MaterialsIO.
    Each new parser must implement the :meth:`parse`, :meth:`version`,
    and :meth:`implementors` functions.
    The :meth:`group` method should be overrode to generate smart groups of file (e.g., associating
    the inputs and outputs to the same calculation)
    :meth:`citations` can be used if there are papers that should be cited if the parser is used
    as part of a scientific publication.

    See `MaterialsIO Contributor Guide
    <https://materialsio.readthedocs.io/en/latest/contributor-guide.html>`_
    for further details.
    """

    def parse_directory(self, path: str, context: dict = None) -> Iterator[Tuple[Tuple[str], dict]]:
        """Run a parser on all appropriate files in a directory

        Skips files that throw exceptions while parsing

        Args:
            path (str): Root of directory to parser
            context (dict): Context about the files
        Yields:
            ([str], dict): Tuple of the group identity and the string
        """

        # Iterate over all directories
        for root, dirs, files in os.walk(path):
            # Generate the full paths for all of the contents
            full_paths = map(lambda x: os.path.join(root, x), files + dirs)

            # Parse each identified group
            for group in self.group(full_paths, context):
                yield (group, self.parse(group, context))

    @abstractmethod
    def parse(self, group: List[str], context: dict = None) -> dict:
        """Extract metadata from a group of files

        A group of files is a set of 1 or more files that describe the same object, and will be
        be used together to create s single summary record.

        Arguments:
            group (list of str):  A list of one or more files that should be parsed together
            context (dict): Context about the files

        Returns:
            (dict): The parsed results, in JSON-serializable format.
        """

    def parse_as_unit(self, files: List[str]) -> dict:
        """Parse a group of files and merge their metadata

        Used if each file in a group are parsed separately, but the resultant metadata
        should be combined after parsing.

        Args:
            files ([str]): List of files to parse
        Returns:
            (dict): Metadata summary from
        """

        # Initialize output dictionary
        metadata = {}

        # Loop over all files
        for group in self.group(files):
            try:
                record = self.parse(group)
                print(record)
            except Exception as exc:
                raise exc
                continue
            metadata = dict_merge(metadata, record)
        return metadata

    def group(self, files: Iterable[str], context: dict = None) -> Iterator[Tuple[str, ...]]:
        """Identify a groups of files that should be parsed together

        Args:
            files ([str]): List of paths, which could include both files and directories
            context (dict): Context about the files
        Yields:
            ((str)): Groups of files
        """

        return zip(f for f in files if not os.path.isdir(f))

    def citations(self) -> List[str]:
        """Citation(s) and reference(s) for this parser

        Returns:
            (list of str): each element should be a string citation in BibTeX format.
        """
        return []

    @abstractmethod
    def implementors(self) -> List[str]:
        """List of implementors of the parser

        These people are the points-of-contact for addressing errors or modifying the parser

        Returns:
            (list) each element should either be a string with author name (e.g.,
                "Anubhav Jain") or a dictionary  with required key "name" and other
                keys like "email" or "institution" (e.g., {"name": "Anubhav
                Jain", "email": "ajain@lbl.gov", "institution": "LBNL"}).
        """

    @abstractmethod
    def version(self) -> str:
        """Return the version of the parser

        Returns:
            (str): Version of the parser
        """

    @property
    def schema(self) -> dict:
        """Schema for the output of the parser"""
        return {
            "$schema": "http://json-schema.org/schema#"
        }


class BaseSingleFileParser(BaseParser):
    """Base class for parsers that only ever considers a single file at a time

    Instead of implementing :meth:`parse`, implement :meth:`_parse_file`"""

    @abstractmethod
    def _parse_file(self, path, context=None):
        """Generate the metadata for a single file

        Args:
            path (str): Path to the file
            context (dict): Optional context information about the file
        Returns:
            (dict): Metadata for the file
        """

    def parse(self, group, context=None):
        # Error catching: allows for single files to passed not as list
        if isinstance(group, str):
            return self._parse_file(group, context)

        # Assumes that the group must have exactly one file
        if len(group) > 1:
            raise ValueError('Parser only takes a single file at a time')

        return self._parse_file(group[0], context)
