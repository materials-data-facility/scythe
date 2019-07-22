"""Base classes for adapters"""

from abc import ABC, abstractmethod
from typing import Any, Union
import json

from materials_io.base import BaseParser


class BaseAdapter(ABC):
    """Template for tools that transform metadata into a new form

    ## Implementing a New Adapter

    Adapters must fulfill a single operation, :meth:`transform`, which renders
    metadata from one of the MaterialsIO parsers into a new form.

    The `transform` function can return `None` or throw an Exception to reject
    a particular entry.

    """

    @abstractmethod
    def transform(self, metadata: dict) -> Any:
        """Process metadata into a new form

        Args:
            metadata (dict): Metadata to transform
        Returns:
            Metadata in a new form, can be any type of object
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
        """Version of the parser that an adapter was created for"""
        return None


class NOOPAdapter(BaseAdapter):
    """Adapter that does not alter the output data

    Used for testing purposes"""

    def transform(self, metadata: dict) -> dict:
        return metadata


class SerializeAdapter(BaseAdapter):
    """Converts the metadata to a string by serializing with JSON"""

    def transform(self, metadata: dict) -> str:
        return json.dumps(metadata)
