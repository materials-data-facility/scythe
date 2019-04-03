from materials_io.dft import DFTParser
from shutil import copy
from glob import glob
import tarfile
import pytest
import os

vasp_tar = os.path.join(os.path.dirname(__file__), 'data',
                        'vasp', 'ALNi_static_LDA.tar.gz')


@pytest.fixture
def vasp_dir(tmpdir):
    """Unpack VASP tar into a temporary directory"""
    with tarfile.open(vasp_tar) as fp:
        fp.extractall(tmpdir)
    return str(tmpdir)


@pytest.fixture
def parser():
    return DFTParser(quality_report=False)


@pytest.fixture
def multi_vasp_dir(vasp_dir):
    """VASP directory with two calcualtions with different extensions"""
    for f in glob(os.path.join(os.path.join(vasp_dir, 'ALNi_static_LDA'), '*')):
        if os.path.isfile(f):
            copy(f, f + '.2')
    return str(vasp_dir)


def test_single_vasp_calc(parser, vasp_dir):
    groups = list(parser.group(vasp_dir))
    assert len(groups) == 1
    assert len(groups[0]) == 8  # All the files

    metadata = list(parser.parse_directory(vasp_dir))
    assert len(metadata) == 1
    print(metadata[0])
    assert isinstance(metadata[0], tuple)
    assert isinstance(metadata[0][0], list)
    assert isinstance(metadata[0][1], dict)


def test_multivasp_calc(parser: DFTParser, multi_vasp_dir):
    groups = list(parser.group(multi_vasp_dir))
    assert len(groups) == 2
    assert [len(g) for g in groups] == [8, 8]  # All the files, twice

    metadata = list(parser.parse_directory(multi_vasp_dir))
    assert len(metadata) == 2
    assert isinstance(metadata[0][0], list)
    assert isinstance(metadata[0][1], dict)