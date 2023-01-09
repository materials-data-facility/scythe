from scythe.base import BaseSingleFileExtractor
from tableschema.exceptions import CastError
from tableschema import Table
from typing import List
import logging

logger = logging.getLogger(__name__)


class CSVExtractor(BaseSingleFileExtractor):
    """Describe the contents of a comma-separated value (CSV) file

    The context dictionary for the CSV parser includes several fields:
        - ``schema``: Dictionary defining the schema for this dataset, following that of
          FrictionlessIO
        - ``na_values``: Any values that should be interpreted as missing
    """

    def __init__(self, return_records=True, **kwargs):
        """
        Args:
             return_records (bool): Whether to return each row in the CSV file
        Keyword:
            All kwargs as passed to `TableSchema's infer <https://github.com/frictionlessdata/tableschema-py#infer>`_ method
        """
        self.return_records = return_records
        self.infer_kwargs = kwargs

    def _extract_file(self, path: str, context=None):
        # Set the default value
        if context is None:
            context = dict()

        # Load in the table
        table = Table(path, schema=context.get('schema', None))

        # Infer the table's schema
        table.infer(**self.infer_kwargs)

        # Add missing values
        if 'na_values' in context:
            if not isinstance(context['na_values'], list):
                raise ValueError('context["na_values"] must be a list')
            table.schema.descriptor['missingValues'] = sorted(set([''] + context['na_values']))
            table.schema.commit()

        # Store the schema
        output = {'schema': table.schema.descriptor}

        # If desired, store the data
        if self.return_records:
            headers = table.schema.headers
            records = []
            failed_records = 0
            for row in table.iter(keyed=False, cast=False):
                try:
                    row = table.schema.cast_row(row)
                except CastError:
                    failed_records += 1

                # TODO (wardlt): Use json output from tableschema once it's supported
                #  https://github.com/frictionlessdata/tableschema-py/issues/213
                records.append(eval(repr(dict(zip(headers, row)))))
            if failed_records > 0:
                logger.warning(f'{failed_records} records failed casting with schema')
            output['records'] = records

        return output

    def implementors(self) -> List[str]:
        return ['Logan Ward']

    def citations(self) -> List[str]:
        return ["https://github.com/frictionlessdata/tableschema-py"]

    def version(self) -> str:
        return '0.0.1'
