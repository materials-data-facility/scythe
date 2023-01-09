from mdf_toolbox import translate_json
import xmltodict

from scythe.base import BaseSingleFileExtractor


class XMLExtractor(BaseSingleFileExtractor):
    """Extracts fields in XML into a user-defined new schema in JSON."""

    def _extract_file(self, path, context=None):
        """Context used:
            mapping (dict): Required. The mapping of desired_fields: existing_fields,
                    using dot notation. For example:
                    {"good_schema.good_field": "oldSchema.longpath.nestedDicts.old_field"}
            na_values (list of str): Values to treat as N/A. Default None.
        """
        if not context.get("mapping"):
            raise ValueError("Mapping is required for the XMLExtractor.")
        with open(path) as f:
            file_json = xmltodict.parse(f.read())
        return translate_json(file_json, context["mapping"],
                              na_values=context.get("na_values", None))

    def implementors(self):
        return ['Jonathon Gaff']

    def version(self):
        return '0.0.1'
