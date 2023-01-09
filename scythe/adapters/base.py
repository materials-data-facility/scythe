"""Base classes for adapters"""

import json
from abc import abstractmethod
from typing import Any, Union

import numpy as np

from scythe.base import BaseExtractor


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

    def check_compatibility(self, parser: BaseExtractor) -> bool:
        """Evaluate whether an adapter is compatible with a certain parser

        Args:
            parser (BaseExtractor): Parser to evaluate
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


class GreedySerializeAdapter(BaseAdapter):
    """Converts the metadata to a string by serializing with JSON, making some (hopefully) informed
    choices about what to do with various types commonly seen, and otherwise reporting that the
    data type could not be serialized. May not work in all situations, but should cover a large
    number of cases."""
    @staticmethod
    def default(o):
        success = False
        if isinstance(o, np.void):
            return None
        elif isinstance(o, (np.ndarray, np.generic)):
            return o.tolist()
        elif isinstance(o, bytes):
            try:
                return o.decode()
            except UnicodeDecodeError:
                pass

        if not success:
            type_name = o.__class__.__name__
            return f"<<Unserializable type: {type_name}>>"

    def transform(self, metadata: dict, context=None) -> str:
        s = json.dumps(metadata, default=GreedySerializeAdapter.default)
        return s
