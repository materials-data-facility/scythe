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
    res = parser.parse([file_path('01_test-EDS_spectrum.dm3')])

    assert res['electron_microscopy']['General'] == {
        'date': {'value': '2016-08-08'},
        'original_filename': {'value': '01_test-EDS_spectrum.dm3'},
        'time': {'value': '21:46:19'},
        'title': {'value': 'EDS Spectrum'}
    }
    assert res['electron_microscopy']['General_EM'] == {
        'acquisition_mode': {'value': 'STEM'},
        'beam_current': {'value': 0.0, 'units': 'NanoA'},
        'beam_energy': {'value': 200.0, 'units': 'KiloEV'},
        'magnification_indicated': {'value': 320000.0, 'units': 'UNITLESS'},
        'microscope_name': {'value': 'FEI Titan'}, 'stage_position': {
            'tilt_alpha': {'value': 24.950478513002935, 'units': 'DEG'},
            'x': {'value': -0.480393, 'units': 'MilliM'},
            'y': {'value': 0.057116, 'units': 'MilliM'},
            'z': {'value': 0.028449299999999997, 'units': 'MilliM'}},
        'acquisition_software_name': {'value': 'DigitalMicrograph'},
        'emission_current': {'value': 0.0, 'units': 'MicroA'},
        'accelerating_voltage': {'value': 200.0, 'units': 'KiloEV'},
        'acquisition_software_version': {'value': '2.31.734.0'}}
    assert res['electron_microscopy']['TEM'] == {
        'camera_length': {'value': 135.0, 'units': 'MilliM'},
        'spherical_aberration_coefficient': {'value': 0.0, 'units': 'MilliM'},
        'operation_mode': {'value': 'SCANNING'},
        'imaging_mode': {'value': 'DIFFRACTION'},
        'illumination_mode': {'value': 'STEM NANOPROBE'},
        'acquisition_mode': {'value': 'Parallel dispersive'},
        'acquisition_format': {'value': 'Spectrum'},
        'acquisition_signal': {'value': 'X-ray'}}
    assert res['electron_microscopy']['EDS'] == {
        'azimuth_angle': {'value': 45.0, 'units': 'DEG'},
        'elevation_angle': {'value': 18.0, 'units': 'DEG'},
        'energy_resolution_MnKa': {'value': 130.0, 'units': 'EV'},
        'live_time': {'value': 3.806, 'units': 'SEC'},
        'real_time': {'value': 4.233, 'units': 'SEC'},
        'detector_type': {'value': 'SIUTW'},
        'dispersion_per_channel': {'value': 5.0, 'units': 'EV'},
        'incidence_angle': {'value': 90.0, 'units': 'DEG'},
        'solid_angle': {'value': 0.7, 'units': 'SR'},
        'stage_tilt': {'value': 0.0, 'units': 'DEG'}}
    assert res['image'] == {'shape': [4096]}

    res = parser.parse([file_path('02_EDS_SI_Titan.dm4')])
    assert res['electron_microscopy']['General'] == {
        'date': {'value': '2019-05-21'},
        'original_filename': {'value': '02_EDS_SI_Titan.dm4'},
        'time': {'value': '15:49:18'}, 'title': {'value': 'EDS Spectrum Image'}}
    assert res['electron_microscopy']['General_EM'] == {
        'acquisition_mode': {'value': 'STEM'},
        'beam_current': {'value': 0.0, 'units': 'NanoA'},
        'beam_energy': {'value': 300.0, 'units': 'KiloEV'},
        'magnification_indicated': {'value': 910000.0, 'units': 'UNITLESS'},
        'microscope_name': {'value': 'Titan80-300_D3094'},
        'stage_position': {
            'tilt_alpha': {'value': 15.208992784409162, 'units': 'DEG'},
            'tilt_beta': {'value': -0.88000014796348, 'units': 'DEG'},
            'x': {'value': 0.013455, 'units': 'MilliM'},
            'y': {'value': 0.137812, 'units': 'MilliM'},
            'z': {'value': 0.0009226799999999999, 'units': 'MilliM'}},
        'acquisition_software_name': {'value': 'DigitalMicrograph'},
        'emission_current': {'value': 0.0, 'units': 'MicroA'},
        'accelerating_voltage': {'value': 300.0, 'units': 'KiloEV'},
        'detector_name': {'value': 'GIF CCD'},
        'acquisition_software_version': {'value': '2.32.888.0'}}
    assert res['electron_microscopy']['TEM'] == {
        'camera_length': {'value': 77.0, 'units': 'MilliM'},
        'spherical_aberration_coefficient': {'value': 1.0, 'units': 'MilliM'},
        'operation_mode': {'value': 'SCANNING'},
        'imaging_mode': {'value': 'DIFFRACTION'},
        'illumination_mode': {'value': 'STEM NANOPROBE'},
        'acquisition_mode': {'value': 'Parallel dispersive'},
        'acquisition_format': {'value': 'Spectrum image'},
        'acquisition_signal': {'value': 'X-ray'}}
    assert res['electron_microscopy']['EDS'] == {
        'azimuth_angle': {'value': 45.0, 'units': 'DEG'},
        'elevation_angle': {'value': 40.0, 'units': 'DEG'},
        'energy_resolution_MnKa': {'value': 130.0, 'units': 'EV'},
        'live_time': {'value': 1.0, 'units': 'SEC'},
        'real_time': {'value': 0.5, 'units': 'SEC'},
        'detector_type': {'value': 'SIUTW'},
        'incidence_angle': {'value': 90.0, 'units': 'DEG'},
        'solid_angle': {'value': 0.002, 'units': 'SR'},
        'stage_tilt': {'value': 0.0, 'units': 'DEG'}}
    assert res['image'] == {'shape': [100, 4096]}


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
        'title': {'value': 'EELS Spectrum Image'}}
    assert res['electron_microscopy']['General_EM'] == {
        'acquisition_mode': {'value': 'STEM'},
        'beam_current': {'value': 0.0, 'units': 'NanoA'},
        'beam_energy': {'value': 300.0, 'units': 'KiloEV'},
        'convergence_angle': {'value': 13.0, 'units': 'MilliRAD'},
        'magnification_indicated': {'value': 57000.0, 'units': 'UNITLESS'},
        'microscope_name': {'value': 'FEI Tecnai Remote'}, 'stage_position': {
            'tilt_alpha': {'value': 1.8231688928401335, 'units': 'DEG'},
            'tilt_beta': {'value': -2.420001839294058, 'units': 'DEG'},
            'x': {'value': -0.035997, 'units': 'MilliM'},
            'y': {'value': -0.0107027, 'units': 'MilliM'},
            'z': {'value': -0.14221899999999998, 'units': 'MilliM'}},
        'dwell_time': {'value': 0.5, 'units': 'SEC'},
        'acquisition_software_name': {'value': 'DigitalMicrograph'},
        'emission_current': {'value': 0.0, 'units': 'MicroA'},
        'accelerating_voltage': {'value': 300.0, 'units': 'KiloEV'},
        'exposure_time': {'value': 0.5, 'units': 'SEC'},
        'acquisition_software_version': {'value': '2.32.888.0'}}
    assert res['electron_microscopy']['TEM'] == {
        'camera_length': {'value': 60.0, 'units': 'MilliM'},
        'spherical_aberration_coefficient': {'value': 1.0, 'units': 'MilliM'},
        'operation_mode': {'value': 'SCANNING'},
        'imaging_mode': {'value': 'DIFFRACTION'},
        'illumination_mode': {'value': 'STEM NANOPROBE'},
        'acquisition_mode': {'value': 'Parallel dispersive'},
        'acquisition_format': {'value': 'Spectrum image'},
        'acquisition_signal': {'value': 'EELS'},
        'acquisition_device': {'value': 'US1000FT 1'}}
    assert res['electron_microscopy']['EELS'] == {
        'aperture_size': {'value': 2.5, 'units': 'MilliM'},
        'collection_angle': {'value': 13.88888931274414, 'units': 'MilliRAD'},
        'number_of_samples': {'value': 1, 'units': 'NUM'},
        'spectrometer_name': {'value': 'GIF Tridiem ER'},
        'dispersion_per_channel': {'value': 0.5, 'units': 'EV'},
        'energy_loss_offset': {'value': 400.0, 'units': 'EV'},
        'drift_tube_voltage': {'value': 400.0, 'units': 'V'},
        'drift_tube_enabled': {'value': True},
        'prism_shift_voltage': {'value': 0.0, 'units': 'V'},
        'prism_shift_enabled': {'value': True},
        'filter_slit_width': {'value': 10.0, 'units': 'EV'},
        'filter_slit_inserted': {'value': False}}
    assert res['image'] == {'shape': [1186, 2048]}


def test_dm3_tecnai(parser):
    eels_mdata = {
        'spectrometer_mode': {'value': 'Spectroscopy'},
        'dispersion_per_channel': {'value': 0.1, 'units': 'EV'},
        'aperture_size': {'value': 3.0, 'units': 'MilliM'},
        'drift_tube_energy': {'value': 0.0, 'units': 'EV'},
        'prism_shift_energy': {'value': -0.0, 'units': 'EV'},
        'total_energy_loss': {'value': 0.0, 'units': 'EV'}
    }

    # parse imaging mode tecnai file
    res = parser.parse([file_path('06_Titan_Tecnai_image.dm3')])

    assert res['electron_microscopy']['General'] == {
        'date': {'value': '2019-03-13'},
        'original_filename': {'value': '06_Titan_Tecnai_image.dm3'},
        'time': {'value': '15:02:56'},
        'title': {'value': '04 - 40um obj - 8100x'}
    }
    assert res['electron_microscopy']['General_EM'] == {
        'acquisition_mode': {'value': 'TEM'},
        'beam_current': {'value': 0.0, 'units': 'NanoA'},
        'beam_energy': {'value': 300.0, 'units': 'KiloEV'},
        'magnification_indicated': {'value': 8100, 'units': 'UNITLESS'},
        'microscope_name': {'value': 'Titan 300 kV D3188 SuperTwin'},
        'acquisition_software_name': {'value': 'DigitalMicrograph'},
        'magnification_actual': {'value': 10816.0, 'units': 'UNITLESS'},
        'emission_current': {'value': 131.0, 'units': 'MicroA'},
        'accelerating_voltage': {'value': 300.0, 'units': 'KiloEV'},
        'exposure_time': {'value': 1.0, 'units': 'SEC'},
        'stage_position': {
            'x': {'value': 147.847, 'units': 'MicroM'},
            'y': {'value': -132.289, 'units': 'MicroM'},
            'z': {'value': 126.673, 'units': 'MicroM'},
            'tilt_alpha': {'value': 0.65, 'units': 'DEG'},
            'tilt_beta': {'value': 0.0, 'units': 'DEG'}}}
    assert res['electron_microscopy']['TEM'] == {
        'spherical_aberration_coefficient': {'value': 1.2, 'units': 'MilliM'},
        'camera_length': {'value': 0.0, 'units': 'MilliM'},
        'operation_mode': {'value': 'TEM uP SA Zoom Image'},
        'imaging_mode': {'value': 'IMAGING'},
        'illumination_mode': {'value': 'TEM'},
        'acquisition_device': {'value': 'BM-UltraScan'},
        'extractor_voltage': {'value': 4400, 'units': 'V'},
        'defocus': {'value': -0.0, 'units': 'MicroM'},
        'spot_size': {'value': 2, 'units': 'UNITLESS'}}
    assert res['electron_microscopy']['EELS'] == eels_mdata
    assert res['image'] == {'shape': [2048, 2048]}

    # parse diffraction mode tecnai dm3
    res = parser.parse([file_path('07_Titan_Tecnai_diffraction.dm3')])
    assert res['electron_microscopy']['General'] == {
        'date': {'value': '2019-09-19'},
        'original_filename': {'value': '07_Titan_Tecnai_diffraction.dm3'},
        'time': {'value': '18:35:12'}, 'title': {'value': 'CA40_10mrad_CL245'}}
    assert res['electron_microscopy']['General_EM'] == {
        'acquisition_mode': {'value': 'STEM'},
        'beam_current': {'value': 0.0, 'units': 'NanoA'},
        'beam_energy': {'value': 300.0, 'units': 'KiloEV'},
        'magnification_indicated': {'value': 1800000, 'units': 'UNITLESS'},
        'microscope_name': {'value': 'Titan 300 kV D3188 SuperTwin'},
        'acquisition_software_name': {'value': 'DigitalMicrograph'},
        'magnification_actual': {'value': 245.00000000000003,
                                 'units': 'UNITLESS'},
        'emission_current': {'value': 150.0, 'units': 'MicroA'},
        'accelerating_voltage': {'value': 300.0, 'units': 'KiloEV'},
        'exposure_time': {'value': 2.0, 'units': 'SEC'},
        'stage_position': {'x': {'value': -201.9, 'units': 'MicroM'},
                           'y': {'value': 269.484, 'units': 'MicroM'},
                           'z': {'value': 31.231, 'units': 'MicroM'},
                           'tilt_alpha': {'value': 0.64, 'units': 'DEG'},
                           'tilt_beta': {'value': 0.22, 'units': 'DEG'}}}
    assert res['electron_microscopy']['TEM'] == {
        'camera_length': {'value': 245.0, 'units': 'MilliM'},
        'spherical_aberration_coefficient': {'value': 1.2, 'units': 'MilliM'},
        'operation_mode': {'value': 'STEM nP SA Zoom Diffraction'},
        'imaging_mode': {'value': 'DIFFRACTION'},
        'illumination_mode': {'value': 'STEM'},
        'acquisition_device': {'value': 'BM-UltraScan'},
        'extractor_voltage': {'value': 4500, 'units': 'V'},
        'defocus': {'value': 0.082, 'units': 'MicroM'},
        'spot_size': {'value': 8, 'units': 'UNITLESS'}}
    assert res['electron_microscopy']['EELS'] == eels_mdata
    assert res['image'] == {'shape': [2048, 2048]}

    # parse diffraction mode tecnai with no spectrometer info
    res = parser.parse([file_path(
        '08_Titan_diffraction_Tecnai_no_spectrometer.dm3')])
    assert res['electron_microscopy']['General'] == {
        'date': {'value': '2019-03-22'}, 'original_filename': {
            'value': '08_Titan_diffraction_Tecnai_no_spectrometer.dm3'},
        'time': {'value': '14:39:25'}, 'title': {'value': '02-380mm_A'}}
    assert res['electron_microscopy']['General_EM'] == {
        'acquisition_mode': {'value': 'TEM'},
        'beam_current': {'value': 0.0, 'units': 'NanoA'},
        'beam_energy': {'value': 300.0, 'units': 'KiloEV'},
        'microscope_name': {'value': 'Titan 300 kV D3188 SuperTwin'},
        'acquisition_software_name': {'value': 'DigitalMicrograph'},
        'magnification_indicated': {'value': 380.0, 'units': 'UNITLESS'},
        'magnification_actual': {'value': 496.0, 'units': 'UNITLESS'},
        'emission_current': {'value': 140.0, 'units': 'MicroA'},
        'accelerating_voltage': {'value': 300.0, 'units': 'KiloEV'},
        'exposure_time': {'value': 1.0, 'units': 'SEC'},
        'stage_position': {'x': {'value': 357.213, 'units': 'MicroM'},
                           'y': {'value': 40.045, 'units': 'MicroM'},
                           'z': {'value': 13.386, 'units': 'MicroM'},
                           'tilt_alpha': {'value': 2.03, 'units': 'DEG'},
                           'tilt_beta': {'value': 0.38, 'units': 'DEG'}}}
    assert res['electron_microscopy']['TEM'] == {
        'camera_length': {'value': 380.0, 'units': 'MilliM'},
        'spherical_aberration_coefficient': {'value': 1.2, 'units': 'MilliM'},
        'operation_mode': {'value': 'TEM uP SA Zoom Diffraction'},
        'imaging_mode': {'value': 'DIFFRACTION'},
        'illumination_mode': {'value': 'TEM'},
        'acquisition_device': {'value': 'BM-UltraScan'},
        'extractor_voltage': {'value': 4500, 'units': 'V'},
        'defocus': {'value': 0.0, 'units': 'MicroM'},
        'spot_size': {'value': 3, 'units': 'UNITLESS'}}
    assert res['image'] == {'shape': [2048, 2048]}
