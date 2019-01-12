
from mixins import *

class BaseParser(GroupAllMixin, AttributionMixin):
    # Parsing function (required)
    def parse(self, group, context=None):
        """parse() is required. It must take a list of one or more files (group)
        and optionally a dictionary of data context/configuration information (context).
        Accepted context must be documented here. Other fields must be ignored.
        It must return a dictionary or list of dictionaries containing parsed data,
        in JSON-serializable format.
        Arguments:
        group (list of str):  A list of one or more files to parse as a unit.
        context (dict): An optional data context/configuration dictionary. Default None.
        Returns:
        dict or list of dict: The parsed results, in JSON-serializable format.
        """

        return {}

    # Validity-check function
    def is_valid(self, group, context=None):
        """is_valid() checks if a file can be used with parse(). It is recommended to include
        for ease of use, but it not required.
        This function must take the same arguments as parse(). It must return a boolean
        to indicate if the group is valid for the parser.
        Arguments:
        group (list of str):  A list of one or more files to parse as a unit.
        context (dict): An optional data context/configuration dictionary. Default None.
        Returns:
        bool: True when the group can be parsed by the parser. False otherwise.
        """
        try:
            res = parse(group, context=context)
            if not res:
                raise ValueError
        except Exception:
            return False
        else:
            return True
    

