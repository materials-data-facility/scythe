"""Base classes for adapters"""

from abc import abstractmethod
from typing import Any, Union
import json

from materials_io.base import BaseParser


class BaseAdapter:
    """Template for tools that transform metadata into a new form"""

    @abstractmethod
    def transform(self, metadata: dict, context: Union[None, dict] = None) -> Any:
        """Process metadata into a new form

        Args:
            metadata (dict): Metadata to transform
            context (dict): Any context information used during transformation
        Returns:
            Metadata in a new form, can be any type of object.
            ``None`` corresponding
        """

    def check_compatibility(self, parser: BaseParser) -> bool:
        """Evaluate whether an adapter is compatible with a certain parser

        Args:
            parser (BaseParser): Parser to evaluate
        Returns:
            (bool) Whether this parser is compatible
        """

        if self.version() is None:
            return True
        else:
            my_version = tuple(int(x) for x in self.version().split('.'))
            their_version = tuple(int(x) for x in parser.version().split('.'))
            return my_version == their_version

    def version(self) -> Union[None, str]:
        """Version of the parser that an adapter was created for

        Returns:
            (str) Version of parser this adapter was designed for,
                or ``None`` if not applicable
            """
        return None


class NOOPAdapter(BaseAdapter):
    """Adapter that does not alter the output data

    Used for testing purposes"""

    def transform(self, metadata: dict, context=None) -> dict:
        return metadata


class SerializeAdapter(BaseAdapter):
    """Converts the metadata to a string by serializing with JSON"""

    def transform(self, metadata: dict, context=None) -> str:
        return json.dumps(metadata)
