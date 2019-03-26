from abc import ABC, abstractmethod
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

    See documentation for further details: TBD.
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

    @abstractmethod
    def parse(self, group, context=None):
        """Extract metadata from a group of files

        Arguments:
            group (list of str):  A list of one or more files that describe the same object
            context (dict): An optional data context/configuration dictionary. Default None.

        Returns:
            (list of dict): The parsed results, in JSON-serializable format.
        """
        pass

    def group(self, root, context=None):
        """Identify sets files in a directory that are related to each other

        Args:
            root (str): Path to a directory
            context (dict): An optional data context/configuration dictionary. Default None.
        Yields:
            ([str]): Groups of files
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
        pass

    @abstractmethod
    def version(self):
        """Return the version of the parser

        Returns:
            (str): Version of the parser
        """
        pass

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
            context (dict):
        """
        pass

    def parse(self, group, context=None):
        return [self._parse_file(f, context) for f in group]
