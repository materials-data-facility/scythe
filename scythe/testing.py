"""Parsers used for testing purposes"""

from scythe.base import BaseExtractor
from typing import Iterable
import os


class NOOPExtractor(BaseExtractor):
    """Determine whether files exist, used for debugging

    Is not truly a "noop" parser, as it does perform a check as to whether the parser
    has access to a certain file. It is more a "check if the parser could run and then do
    nothing" parser.
    """

    def extract(self, group: Iterable[str], context: dict = None):
        return dict((f, os.path.exists(f)) for f in group)

    def version(self):
        return '0.0.1'

    def implementors(self):
        return ['Logan Ward <lward@anl.gov>']
