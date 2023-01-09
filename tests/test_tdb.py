import os

from mdf_toolbox import insensitive_comparison as eqi
import pytest

from scythe.tdb import TDBExtractor


@pytest.fixture
def test_files():
    return [os.path.join(os.path.dirname(__file__), 'data', 'tdb', 'PbSSeTe_Na.TDB'),
            os.path.join(os.path.dirname(__file__), 'data', 'tdb', 'test_AuSi.TDB'),
            os.path.join(os.path.dirname(__file__), 'data', 'tdb', 'test_PbTe.TDB')]


@pytest.fixture
def fail_file():
    return os.path.join(os.path.dirname(__file__), 'data', 'fail_file.dat')


@pytest.fixture
def extractor():
    return TDBExtractor()


def test_tdb(extractor, test_files, fail_file):
    # Run test extractions
    output0 = extractor.parse(test_files[0])
    assert eqi(output0["material"]["composition"], "VaPbSNaTeSe", string_insensitive=True)
    assert eqi(output0["calphad"]["phases"], ['LIQUID', 'FCC_A1', 'HALITE', 'HEXAGONAL_A8',
                                              'ORTHORHOMBIC_S', 'BCC_A2', 'NA2TE', 'NATE', 'NATE3',
                                              'NA2SE', 'NASE', 'NASE2', 'NA2S', 'NAS', 'NAS2'])
    output1 = extractor.parse(test_files[1])
    assert eqi(output1["material"]["composition"], "SiVaAu", string_insensitive=True)
    assert eqi(output1["calphad"]["phases"], ['LIQUID', 'BCC_A2', 'CBCC_A12', 'CUB_A13',
                                              'DIAMOND_A4', 'FCC_A1', 'HCP_A3', 'HCP_ZN'])
    output2 = extractor.parse(test_files[2])
    assert eqi(output2["material"]["composition"], "TeVaPb", string_insensitive=True)
    assert eqi(output2["calphad"]["phases"], ['LIQUID', 'PBTE', 'HEXAGONAL_A8', 'RHOMBOHEDRAL_A7'])

    # Test failure modes
    with pytest.raises(Exception):
        extractor.parse(fail_file)
