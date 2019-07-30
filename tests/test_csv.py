from materials_io.csv import CSVParser
import os

csv_file = os.path.join(os.path.dirname(__file__), 'data', 'test.csv')


def test_csv():
    p = CSVParser()

    # Test with records
    output = p.parse([csv_file])
    assert len(output['records']) == 3
    assert isinstance(output['records'][0], dict)
    assert output['schema'] == {'fields': [{'name': 'city', 'type': 'string',
                                            'format': 'default'},
                                           {'name': 'location', 'type': 'geopoint',
                                            'format': 'default'}],
                                'missingValues': ['']}

    # Test without records
    p.return_records = False
    assert 'records' not in p.parse([csv_file])

    # Just run the other operations
    assert any('https://github.com/frictionlessdata/tableschema-py' in x for x in p.citations())
    p.implementors()
    p.version()
