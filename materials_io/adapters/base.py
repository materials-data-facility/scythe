"""Base classes for adapters"""

from abc import ABC, abstractmethod
from typing import Any
import json


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


class NOOPAdapter(BaseAdapter):
    """Adapter that does not alter the output data

    Used for testing purposes"""

    def transform(self, metadata: dict) -> dict:
        return metadata


class SerializeAdapter(BaseAdapter):
    """Converts the metadata to a string by serializing with JSON"""

    def transform(self, metadata: dict) -> str:
        return json.dumps(metadata)
