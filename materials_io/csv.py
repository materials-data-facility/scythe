from materials_io.base import BaseSingleFileParser
from tableschema import Table
from typing import List


class CSVParser(BaseSingleFileParser):
    """Reads tabular data files, such as CSV"""

    def __init__(self, return_records=True, **kwargs):
        """
        Args:
             return_records (bool): Whether to return each row in the CSV file
        Keyword:
            All kwargs as passed to `TableSchema's infer <https://github.com/frictionlessdata/tableschema-py#infer>`_
            method
        """
        self.return_records = return_records
        self.infer_kwargs = kwargs

    def _parse_file(self, path: str, context=None):
        table = Table(path)

        # Infer the table's schema
        output = {'schema': table.infer(**self.infer_kwargs)}

        # If desired, store the data
        if self.return_records:
            output['records'] = table.read(keyed=True)

        return output

    def implementors(self) -> List[str]:
        return ['Logan Ward']

    def citations(self) -> List[str]:
        return ["https://github.com/frictionlessdata/tableschema-py"]

    def version(self) -> str:
        return '0.0.1'
