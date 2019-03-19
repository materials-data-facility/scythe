from abc import ABC, abstractmethod

import os


class BaseParser(ABC):
    """Abstract base class for a file parser

    This class defines the interface for all parsers in MaterialsIO.
    Each new parser must implement the :meth:`parse` and :meth:`implementors` functions.
    The :meth:`is_valid` method should be overrode if fast methods for assessing compatibility
    (e.g., checking headers) are possible.
    The :meth:`group` method should be overrode to generate smart groups of file (e.g., associating
    the inputs and outputs to the same calculation)
    :meth:`citations` can be used if there are papers that should be cited if the parser is used
    as part of a scientific publication.

    See documentation for further details: TBD.
    """

    @abstractmethod
    def parse(self, group, context=None):
        """Extract metadata from a group of files

        Arguments:
            group (list of str):  A list of one or more files to parse as a unit.
            context (dict): An optional data context/configuration dictionary. Default None.

        Returns:
            (list of dict): The parsed results, in JSON-serializable format.
        """
        pass

    def is_valid(self, group, context=None):
        """Determine whether a group of files is compatible with this parser

        Arguments:
            group (list of str):  A list of one or more files to parse as a unit.
            context (dict): An optional data context/configuration dictionary. Default None.

        Returns:
            (bool): Whether the group can be parsed by the parser
        """
        try:
            res = self.parse(group, context=context)
            if not res:
                raise ValueError
        except Exception:
            return False
        else:
            return True

    def group(self, root, config=None):
        """Identify sets files in a directory that are related to each other

        Args:
            root (str): Path to a direct
        Yields:
            (list of str): Groups of files
        """

        for path, dirs, files in os.walk(root):
            for f in files:
                yield [os.path.join(path, f)]

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
