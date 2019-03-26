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

    def parse_directory(self, path, context=None):
        """Run a parser on all appropriate files in a directory

        Skips files that throw exceptions while parsing

        Args:
            path (str): Root of directory to parser
            context (dict): An optional data context/configuration dictionary. Default None.
        Yields:
            ([str], [dict]): Tuple of the group identity and the string
        """

        # Run the parsing
        for group in self.group(path, context):
            try:
                yield group, self.parse(group, context)
            except Exception:
                continue

    def parse_as_unit(self, files):
        """Parse a group of files and merge their metadata

        Used if each file in a group are parsed separately, but the resultant metadata
        should be combined after parsing.

        Args:
            files ([str]): List of files to parse
        Returns:
            (dict): Metadata summary from
        """

        metadata = {}

        # TODO (lw): @jgaff Do we need grouping functionality, or just loop over each file?
        for f in files:
            try:
                record = self.parse(f)
            except Exception:
                continue
            else:
                metadata = dict_merge(metadata, record)
        return metadata

    @abstractmethod
    def parse(self, group, context=None) -> dict:
        """Extract metadata from a group of files

        A group of files is a set of 1 or more files that describe the same object, and will be
        be used together to create s single summary record.

        Arguments:
            group (list of str):  A list of one or more files that should be parsed together
            context (dict): An optional data context/configuration dictionary

        Returns:
            (dict): The parsed results, in JSON-serializable format.
        """

    def group(self, root, context=None):
        """Identify sets files in a directory that should be parsed together

        Args:
            root (str): Path to a directory
            context (dict): An optional data context/configuration dictionary.
        Yields:
            ((str)): Groups of files
        """

        for path, dirs, files in os.walk(root):
            for f in files:
                yield (os.path.join(path, f),)

    def citations(self):
        """Citation(s) and reference(s) for this parser

        Returns:
            (list of str): each element should be a string citation in BibTeX format.
        """
        return []

    @abstractmethod
    def implementors(self):
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
