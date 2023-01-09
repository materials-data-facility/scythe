from scythe.crystal_structure import CrystalStructureExtractor
from math import isclose
import pytest
import os


@pytest.fixture
def cif():
    return os.path.join(os.path.dirname(__file__), 'data', 'cif', '1548397.cif')


@pytest.fixture
def parser():
    return CrystalStructureExtractor()


def test_cif(parser, cif):
    output = parser.extract(cif)

    # Check the volume and number of atoms, which is a float
    assert isclose(output['crystal_structure']['volume'], 101836.44086588411)
    assert isclose(output['crystal_structure']['number_of_atoms'], 5070.0)

    # Check everything else
    del output['crystal_structure']['volume']
    del output['crystal_structure']['number_of_atoms']
    assert output == {'material': {'composition': 'Co270H1680C1872N324O924'},
                      'crystal_structure': {'space_group_number': 146,
                                            'stoichiometry': 'A45B54C154D280E312'}}
