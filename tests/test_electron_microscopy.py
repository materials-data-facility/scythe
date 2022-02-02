import pytest
import os

from materials_io.electron_microscopy import ElectronMicroscopyParser


def file_path(fname):
    return os.path.join(os.path.dirname(__file__),
                        'data', 'electron_microscopy', fname)


@pytest.fixture
def parser():
    return ElectronMicroscopyParser()


# TODO (lw): Our parser does not actually get anything from these files
# Update 1/15/20 (JG): EM parser now parses image data (still no EM data though)
def test_dm3(parser):
    res = parser.parse([file_path('test-1.dm3')])
    assert res['image']['shape'] == [2]
    assert res['electron_microscopy']['General'] == {
        'original_filename': {'value': 'test-1.dm3'},
        'title': {'value': 'test'}
    }


def test_dm4(parser):
    res = parser.parse([file_path('test-1.dm4')])
    assert res['image']['shape'] == [2, 2]
    assert res['electron_microscopy']['General'] == {
        'original_filename': {'value': 'test-1.dm4'},
        'title': {'value': 'test'}
    }


def test_eds(parser):
    res = parser.parse([file_path('test-EDS_spectrum.dm3')])

    assert res['electron_microscopy']['General'] == {
        'date': {'value': '2016-08-08'},
        'original_filename': {'value': 'test-EDS_spectrum.dm3'},
        'time': {'value': '21:46:19'},
        'title': {'value': 'EDS Spectrum'}
    }
    assert res['electron_microscopy']['General_EM'] == {
        'acquisition_mode': {'value': 'STEM'},
        'beam_current': {'value': 0.0, 'units': 'NanoA'},
        'beam_energy': {'value': 200.0, 'units': 'KiloEV'},
        'magnification_indicated': {'value': 320000.0, 'units': 'UNITLESS'},
        'microscope_name': {'value': 'FEI Titan'},
        'stage_position': {
            'tilt_alpha': {'value': 24.950478513002935, 'units': 'DEG'},
            'x': {'value': -0.480393, 'units': 'MilliM'},
            'y': {'value': 0.057116, 'units': 'MilliM'},
            'z': {'value': 0.028449299999999997, 'units': 'MilliM'}}
    }
    assert res['electron_microscopy']['TEM'] == {
        'camera_length': {'value': 135.0, 'units': 'MilliM'}
    }
    assert res['electron_microscopy']['EDS'] == {
        'azimuth_angle': {'value': 45.0, 'units': 'DEG'},
        'elevation_angle': {'value': 18.0, 'units': 'DEG'},
        'energy_resolution_MnKa': {'value': 130.0, 'units': 'EV'},
        'live_time': {'value': 3.806, 'units': 'SEC'},
        'real_time': {'value': 4.233, 'units': 'SEC'}
    }
    assert res['image'] == {'shape': [4096]}


def test_edax_eds(parser):
    res = parser.parse([file_path('edax_sem_eds_map_dataZeroed.spd')])

    assert res['electron_microscopy']['General'] == {
        'original_filename': {'value': 'edax_sem_eds_map_dataZeroed.spd'},
        'title': {'value': 'EDS Spectrum Image'}
    }
    assert res['electron_microscopy']['General_EM'] == {
        'beam_energy': {'value': 22.0, 'units': 'KiloEV'},
        'stage_position': {'tilt_alpha': {'value': 0.0, 'units': 'DEG'}},
        'elements': {'value': ['Ce', 'Co', 'Cr', 'Fe', 'Gd',
                               'La', 'Mg', 'O', 'Sr']}
    }
    assert res['electron_microscopy']['EDS'] == {
        'azimuth_angle': {'value': 0.0, 'units': 'DEG'},
        'elevation_angle': {'value': 34.0, 'units': 'DEG'},
        'energy_resolution_MnKa': {'value': 126.6025161743164, 'units': 'EV'},
        'live_time': {'value': 2621.43994140625, 'units': 'SEC'}
    }


def test_eels(parser):
    res = parser.parse([file_path('Titan_EELS_SI_dataZeroed.dm3')])
    assert res['electron_microscopy']['General'] == {
        'date': {'value': '2016-04-22'},
        'original_filename': {'value': 'Titan_EELS_SI_dataZeroed.dm3'},
        'time': {'value': '16:34:54'},
        'title': {'value': 'EELS Spectrum Image'}
    }
    assert res['electron_microscopy']['General_EM'] == {
        'acquisition_mode': {'value': 'STEM'},
        'beam_current': {'value': 0.0, 'units': 'NanoA'},
        'beam_energy': {'value': 300.0, 'units': 'KiloEV'},
        'magnification_indicated': {'value': 57000.0, 'units': 'UNITLESS'},
        'microscope_name': {'value': 'FEI Tecnai Remote'},
        'stage_position': {
            'tilt_alpha': {'value': 1.8231688928401335, 'units': 'DEG'},
            'tilt_beta': {'value': -2.420001839294058, 'units': 'DEG'},
            'x': {'value': -0.035997, 'units': 'MilliM'},
            'y': {'value': -0.0107027, 'units': 'MilliM'},
            'z': {'value': -0.14221899999999998, 'units': 'MilliM'}},
        'dwell_time': {'value': 0.5, 'units': 'SEC'}
    }
    assert res['electron_microscopy']['TEM'] == {
        'camera_length': {'value': 60.0, 'units': 'MilliM'}
    }
    assert res['electron_microscopy']['EELS'] == {
        'collection_angle': {'value': 13.88888931274414, 'units': 'MilliRAD'},
        'number_of_samples': {'value': 1, 'units': 'NUM'}
    }
    assert res['image'] == {'shape': [1186, 2048]}
