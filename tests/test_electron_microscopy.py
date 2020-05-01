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
# Update 1/15/20 (JG): EM parser now parses image data (still no EM data though)
def test_dm3(parser, dm3):
    assert parser.parse([dm3]) == {'image': {'shape': [2]}}


def test_dm4(parser, dm4):
    assert parser.parse([dm4]) == {'image': {'shape': [2, 2]}}


def test_eds(parser, eds):
    assert parser.parse([eds]) == {'electron_microscopy': {'acquisition_mode': 'STEM',
                                                           'beam_energy': 200.0,
                                                           'detector': 'EDS',
                                                           'emission_current': 0.0,
                                                           'magnification': 320000.0,
                                                           'microscope': 'FEI Titan',
                                                           'operation_mode': 'SCANNING'},
                                   'image': {'shape': [4096]}}
