from materials_io.ase import AseParser
from math import isclose
import pytest
import os


@pytest.fixture
def ase():
    return os.path.join(os.path.dirname(__file__), 'data', 'gaussian', 'molecule.log')


@pytest.fixture
def parser():
    return AseParser()


def test_ase(parser, ase):
    output = parser.parse(ase)

    # Check the chemical formula
    assert output['chemical_formula'] == "C38H14N8O12"

    # Check the shape of the force outputs. There should be
    # 72 atoms and forces in 3 directions
    assert len(output['forces'][0]) == 72
    assert len(output['forces'][0][0]) == 3

    assert isclose(output['energy'], -76063.21525532556)
