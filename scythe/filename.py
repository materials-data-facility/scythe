import os
import re

from mdf_toolbox import flatten_json

from scythe.base import BaseSingleFileExtractor


class FilenameExtractor(BaseSingleFileExtractor):
    """Extracts metadata in a filename, according to user-supplied patterns."""

    def _extract_file(self, path, context=None):
        """Context used:
            mapping (dict): Required. The mapping of desired_fields: regex_pattern,
                    using dot notation. For example:
                    {"material.composition": "^[a-zA-Z]{3,4}"}
            na_values (list of str): Values to treat as N/A. Default None.
        """
        if not context.get("mapping"):
            raise ValueError("Mapping is required for the FilenameExtractor.")

        record = {}
        filename = os.path.basename(path)
        for json_path, pattern in flatten_json(context["mapping"]).items():
            match = re.search(pattern, filename)
            if match:
                fields = json_path.split(".")
                last_field = fields.pop()
                current_field = record
                # Create all missing fields
                for field in fields:
                    if current_field.get(field) is None:
                        current_field[field] = {}
                    current_field = current_field[field]
                # Add value to end
                current_field[last_field] = match.group()
        return record

    def implementors(self):
        return ['Jonathon Gaff']

    def version(self):
        return '0.0.1'
