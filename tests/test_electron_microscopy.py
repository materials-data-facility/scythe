import pytest
import os

from materials_io.electron_microscopy import ElectronMicroscopyParser


data_file_loc = os.path.join(os.path.dirname(__file__), 'data', 'electron_microscopy')


@pytest.fixture
def dm3():
    return os.path.join(data_file_loc, 'test-1.dm3')


@pytest.fixture
def dm4():
    return os.path.join(data_file_loc, 'test-1.dm4')


@pytest.fixture
def eds():
    return os.path.join(data_file_loc, 'test-EDS_spectrum.dm3')


@pytest.fixture
def parser():
    return ElectronMicroscopyParser()


# TODO (lw): Our parser does not actually get anything from these files
def test_dm3(parser, dm3):
    assert parser.parse([dm3]) == {}


def test_dm4(parser, dm4):
    assert parser.parse([dm4]) == {}


def test_eds(parser, eds):
    assert parser.parse([eds]) == {'electron_microscopy': {'beam_energy': 200.0,
                                                           'magnification': 320000.0,
                                                           'image_mode': 'STEM',
                                                           'detector': 'EDS'}}
