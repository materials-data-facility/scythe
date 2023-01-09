import logging
import re
import json
import pathlib
from typing import Tuple, Dict, Optional

from hyperspy.io import load as hs_load
from traits.trait_base import Undefined

from scythe.base import BaseSingleFileExtractor
from scythe.utils import get_nested_dict_value_by_path as get_val
from scythe.utils import \
    map_dict_values, MappingElements, standardize_unit
from scythe.utils import set_nested_dict_value_with_units as set_val_units

logger = logging.getLogger(__name__)


class ElectronMicroscopyExtractor(BaseSingleFileExtractor):
    """Extract metadata specific to electron microscopy.

    This parser handles any file supported by HyperSpy's I/O capabilities. Extract both the
    metadata interpreted by HyperSpy directly, but also any important values we can pick out
    manually.

    For each value (if it is known), return a subdict with two keys: ``value``, containing the
    actual value of the metadata parameter, and ``unit``, a string containing a unit name from the
    `QUDT <http://www.qudt.org/doc/DOC_VOCAB-UNITS.html>`_ vocabulary. Including a ``unit`` is
    optional, but highly recommended, if it is known.

    The allowed metadata values are controlled by the JSONSchema specification in the
    ``schemas/electron_microscopy.json`` file.
    """

    def _extract_file(self, file_path: str, context: Dict = None) -> Dict:
        self.em = {}
        self.inst_data = None

        # Read file lazily (reduce memory), both HyperSpy-formatted and raw data
        self.hs_data = hs_load(file_path, lazy=True)

        # if hs_data is a list, pull out first for metadata extraction
        if isinstance(self.hs_data, list):
            self.hs_data = self.hs_data[0]

        self.meta = self.hs_data.metadata.as_dictionary()
        self.raw_meta = self.hs_data.original_metadata.as_dictionary()
        self.em['raw_metadata'] = self.raw_meta

        for s in ['General', 'General_EM', 'TEM', 'SEM', 'EDS', 'EELS']:
            self.em[s] = {}

        # call each individual processor
        self._process_hs_data()
        self._dm3_general_info()
        self._dm3_eels_info()
        self._dm3_tecnai_info()
        self._dm3_eds_info()
        self._tia_info()
        self._tiff_info()

        # Remove None/empty values
        for key, val in list(self.em.items()):
            if val is None or val == [] or val == {}:
                self.em.pop(key)

        record = {}
        if self.em:
            record["electron_microscopy"] = self.em

        return record

    def _process_hs_data(self) -> None:
        """Parse metadata that was already extracted from HyperSpy"""
        # Image mode is SEM, TEM, or STEM
        # STEM is a subset of TEM
        if "SEM" in self.meta.get('Acquisition_instrument', {}).keys():
            self.inst = "SEM"
        elif "TEM" in self.meta.get('Acquisition_instrument', {}).keys():
            self.inst = "TEM"
        else:
            self.inst = 'None'

        # HS data
        self.inst_data = get_val(self.meta, ('Acquisition_instrument', self.inst))
        if self.inst_data is not None:
            source = self.inst_data
            dest = self.em

            mapping = [
                MappingElements(
                    source_dict=source, source_path='acquisition_mode',
                    dest_dict=dest, dest_path=('General_EM', 'acquisition_mode'),
                    cast_fn=str, units=None, conv_fn=None, override=False),
                MappingElements(
                    source_dict=source, source_path='beam_current',
                    dest_dict=dest, dest_path=('General_EM', 'beam_current'),
                    cast_fn=float, units='NanoA', conv_fn=None, override=False),
                MappingElements(
                    source_dict=source, source_path='beam_energy',
                    dest_dict=dest, dest_path=('General_EM', 'beam_energy'),
                    cast_fn=float, units='KiloEV', conv_fn=None,
                    override=False),
                MappingElements(
                    source_dict=source, source_path='convergence_angle',
                    dest_dict=dest, dest_path=('General_EM', 'convergence_angle'),
                    cast_fn=float, units='MilliRAD', conv_fn=None,
                    override=False),
                MappingElements(
                    source_dict=source, source_path='microscope',
                    dest_dict=dest, dest_path=('General_EM', 'microscope_name'),
                    cast_fn=str, units=None, conv_fn=None, override=False),
                MappingElements(
                    source_dict=source, source_path='probe_area',
                    dest_dict=dest, dest_path=('General_EM', 'probe_area'),
                    cast_fn=float, units='NanoM2', conv_fn=None,
                    override=False),

                # stage positions
                MappingElements(
                    source_dict=source, source_path=('Stage', 'rotation'), dest_dict=dest,
                    dest_path=('General_EM', 'stage_position', 'rotation'),
                    cast_fn=float, units='DEG', conv_fn=None, override=False),
                MappingElements(
                    source_dict=source, source_path=('Stage', 'tilt_alpha'), dest_dict=dest,
                    dest_path=('General_EM', 'stage_position', 'tilt_alpha'),
                    cast_fn=float, units='DEG', conv_fn=None, override=False),
                MappingElements(
                    source_dict=source, source_path=('Stage', 'tilt_beta'), dest_dict=dest,
                    dest_path=('General_EM', 'stage_position', 'tilt_beta'),
                    cast_fn=float, units='DEG', conv_fn=None, override=False),
                MappingElements(
                    source_dict=source, dest_dict=dest, source_path=('Stage', 'x'),
                    dest_path=('General_EM', 'stage_position', 'x'),
                    cast_fn=float, units='MilliM', conv_fn=None,
                    override=False),
                MappingElements(
                    source_dict=source, source_path=('Stage', 'y'), dest_dict=dest,
                    dest_path=('General_EM', 'stage_position', 'y'),
                    cast_fn=float, units='MilliM', conv_fn=None,
                    override=False),
                MappingElements(
                    source_dict=source, source_path=('Stage', 'z'), dest_dict=dest,
                    dest_path=('General_EM', 'stage_position', 'z'),
                    cast_fn=float, units='MilliM', conv_fn=None,
                    override=False),

                # camera length/working distance
                MappingElements(
                    source_dict=source, source_path='camera_length',
                    dest_dict=dest, dest_path=('TEM', 'camera_length'),
                    cast_fn=float, units='MilliM', conv_fn=None,
                    override=False),
                MappingElements(
                    source_dict=source, source_path='working_distance',
                    dest_dict=dest, dest_path=('SEM', 'working_distance'),
                    cast_fn=float, units='MilliM', conv_fn=None,
                    override=False)]

            # some logic to parse how Zeiss stores floats in their SEM tifs:
            mag = get_val(source, path='magnification')
            if mag and isinstance(mag, str):
                if ' K X' in mag:
                    mag = mag.replace(' K X', '')
                    try:
                        mag = float(mag)
                        mag *= 1000
                    except ValueError:
                        # don't do anything if we can't coerce the value to a float
                        pass

            mapping += [MappingElements(
                source_dict={'magnification': mag}, source_path='magnification',
                dest_dict=dest, dest_path=('General_EM', 'magnification_indicated'),
                cast_fn=float, units='UNITLESS', conv_fn=None,
                override=False)]

            map_dict_values(mapping)

            self._process_hs_detectors()

        source = self.meta
        dest = self.em
        mapping = [
            # Elements present (if known)
            MappingElements(
                source_dict=source, dest_dict=dest, source_path=('Sample', 'elements'),
                dest_path=('General_EM', 'elements'),
                cast_fn=list, units=None, conv_fn=None, override=False),
            # General metadata
            MappingElements(
                source_dict=source, dest_dict=dest,
                source_path=('General', 'date'), dest_path=('General', 'date'),
                cast_fn=str, units=None, conv_fn=None, override=False),
            MappingElements(
                source_dict=source, dest_dict=dest,
                source_path=('General', 'doi'), dest_path=('General', 'doi'),
                cast_fn=str, units=None, conv_fn=None, override=False),
            MappingElements(
                source_dict=source, dest_dict=dest,
                source_path=('General', 'original_filename'),
                dest_path=('General', 'original_filename'),
                cast_fn=str, units=None, conv_fn=None, override=False),
            MappingElements(
                source_dict=source, dest_dict=dest,
                source_path=('General', 'notes'), dest_path=('General', 'notes'),
                cast_fn=str, units=None, conv_fn=None, override=False),
            MappingElements(
                source_dict=source, dest_dict=dest,
                source_path=('General', 'time'), dest_path=('General', 'time'),
                cast_fn=str, units=None, conv_fn=None, override=False),
            MappingElements(
                source_dict=source, dest_dict=dest,
                source_path=('General', 'time_zone'), dest_path=('General', 'time_zone'),
                cast_fn=str, units=None, conv_fn=None, override=False),
            MappingElements(
                source_dict=source, dest_dict=dest,
                source_path=('General', 'title'), dest_path=('General', 'title'),
                cast_fn=str, units=None, conv_fn=None, override=False)]

        map_dict_values(mapping)
        self._process_hs_axes()

    def _process_hs_axes(self) -> None:
        """Parses the HyperSpy signal axis calibrations into a format that can be stored with the
        metadata. Make sure to remove "Undefined" traits from any axis values, since that value
        cannot be serialized to JSON
        """
        axes = self.hs_data.axes_manager.as_dictionary()

        for k, v in axes.items():
            # remove some non-relevant values
            for to_remove in ['_type', 'navigate', 'is_binned']:
                if to_remove in v:
                    del axes[k][to_remove]

            # remove potentially unserializable values from axes:
            for key in v:
                if v[key] is Undefined:
                    v[key] = None

            # attempt to standardize units according to QUDT:
            if 'units' in v:
                axes[k]['units'] = standardize_unit(axes[k]['units'])

        self.em['General']['axis_calibration'] = axes
        self.em['General']['data_dimensions'] = [v['size'] for v in
                                                 self.hs_data.axes_manager.as_dictionary().values()]

    def _process_hs_detectors(self) -> None:
        """Parses HyperSpy-formatted metadata specific to detectors as specified by
        http://hyperspy.org/hyperspy-doc/current/user_guide/metadata_structure.html
        """
        detector_node = get_val(self.inst_data, 'Detector')
        dest_dict = self.em
        mapping = [
            MappingElements(
                source_dict=self.inst_data, source_path='detector_type',
                dest_dict=dest_dict, dest_path=('General_EM', 'detector_name'),
                cast_fn=str, units=None, conv_fn=None, override=False
            )
        ]

        if detector_node is not None:
            mapping += [
                # EDS
                MappingElements(
                    source_dict=detector_node, source_path=('EDS', 'azimuth_angle'),
                    dest_dict=dest_dict, dest_path=('EDS', 'azimuth_angle'),
                    cast_fn=float, units='DEG', conv_fn=None, override=False),
                MappingElements(
                    source_dict=detector_node, source_path=('EDS', 'elevation_angle'),
                    dest_dict=dest_dict, dest_path=('EDS', 'elevation_angle'),
                    cast_fn=float, units='DEG', conv_fn=None, override=False),
                MappingElements(
                    source_dict=detector_node, source_path=('EDS', 'energy_resolution_MnKa'),
                    dest_dict=dest_dict, dest_path=('EDS', 'energy_resolution_MnKa'),
                    cast_fn=float, units='EV', conv_fn=None, override=False),
                MappingElements(
                    source_dict=detector_node, source_path=('EDS', 'live_time'),
                    dest_dict=dest_dict, dest_path=('EDS', 'live_time'),
                    cast_fn=float, units='SEC', conv_fn=None, override=False),
                MappingElements(
                    source_dict=detector_node, source_path=('EDS', 'real_time'),
                    dest_dict=dest_dict, dest_path=('EDS', 'real_time'),
                    cast_fn=float, units='SEC', conv_fn=None, override=False),

                # EELS
                MappingElements(
                    source_dict=detector_node, source_path=('EELS', 'aperture_size'),
                    dest_dict=dest_dict, dest_path=('EELS', 'aperture_size'),
                    cast_fn=float, units='MilliM', conv_fn=None,
                    override=False),
                MappingElements(
                    source_dict=detector_node, source_path=('EELS', 'collection_angle'),
                    dest_dict=dest_dict, dest_path=('EELS', 'collection_angle'),
                    cast_fn=float, units='MilliRAD', conv_fn=None,
                    override=False),
                MappingElements(
                    source_dict=detector_node, source_path=('EELS', 'dwell_time'),
                    dest_dict=dest_dict, dest_path=('General_EM', 'dwell_time'),
                    cast_fn=float, units='SEC', conv_fn=None, override=False),
                MappingElements(
                    source_dict=detector_node, source_path=('EELS', 'exposure'),
                    dest_dict=dest_dict, dest_path=('General_EM', 'exposure_time'),
                    cast_fn=float, units='SEC', conv_fn=None, override=False),
                MappingElements(
                    source_dict=detector_node, source_path=('EELS', 'frame_number'),
                    dest_dict=dest_dict, dest_path=('EELS', 'number_of_samples'),
                    cast_fn=int, units='NUM', conv_fn=None, override=False),
                MappingElements(
                    source_dict=detector_node, source_path=('EELS', 'spectrometer'),
                    dest_dict=dest_dict, dest_path=('EELS', 'spectrometer_name'),
                    cast_fn=str, units=None, conv_fn=None, override=False),
            ]
        map_dict_values(mapping)

    def _dm3_general_info(self) -> None:
        """Parse commonly-found TEM-related tags in DigitalMicrograph files"""
        # process "Microscope Info"
        base = self.__get_dm3_tag_pre_path() + ('Microscope Info',)
        dest_dict = self.em
        mapping = [
            MappingElements(
                source_dict=self.raw_meta, source_path=base + ('Indicated Magnification',),
                dest_dict=dest_dict, dest_path=('General_EM', 'magnification_indicated'),
                cast_fn=float, units='UNITLESS', conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=base + ('Actual Magnification',),
                dest_dict=dest_dict, dest_path=('General_EM', 'magnification_actual'),
                cast_fn=float, units='UNITLESS', conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=base + ('Cs(mm)',),
                dest_dict=dest_dict, dest_path=('TEM', 'spherical_aberration_coefficient'),
                cast_fn=float, units='MilliM', conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=base + ('STEM Camera Length',),
                dest_dict=dest_dict, dest_path=('TEM', 'camera_length'),
                cast_fn=float, units='MilliM', conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=base + ('Operation Mode',),
                dest_dict=dest_dict, dest_path=('TEM', 'operation_mode'),
                cast_fn=str, units=None, conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=base + ('Imaging Mode',),
                dest_dict=dest_dict, dest_path=('TEM', 'imaging_mode'),
                cast_fn=str, units=None, conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=base + ('Illumination Mode',),
                dest_dict=dest_dict, dest_path=('TEM', 'illumination_mode'),
                cast_fn=str, units=None, conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=base + ('Microscope',),
                dest_dict=dest_dict, dest_path=('General_EM', 'microscope_name'),
                cast_fn=str, units=None, conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=base + ('Stage Position', 'Stage X'),
                dest_dict=dest_dict, dest_path=('General_EM', 'stage_position', 'x'),
                cast_fn=float, units='MilliM', conv_fn=lambda x: x/1000, override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=base + ('Stage Position', 'Stage Y'),
                dest_dict=dest_dict, dest_path=('General_EM', 'stage_position', 'y'),
                cast_fn=float, units='MilliM', conv_fn=lambda x: x / 1000, override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=base + ('Stage Position', 'Stage Z'),
                dest_dict=dest_dict, dest_path=('General_EM', 'stage_position', 'z'),
                cast_fn=float, units='MilliM', conv_fn=lambda x: x / 1000, override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=base + ('Stage Position', 'Stage Alpha'),
                dest_dict=dest_dict, dest_path=('General_EM', 'stage_position', 'tilt_alpha'),
                cast_fn=float, units='DEG', conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=base + ('Stage Position', 'Stage Beta'),
                dest_dict=dest_dict, dest_path=('General_EM', 'stage_position', 'tilt_beta'),
                cast_fn=float, units='DEG', conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=base + ('Emission Current (µA)',),
                dest_dict=dest_dict, dest_path=('General_EM', 'emission_current'),
                cast_fn=float, units='MicroA', conv_fn=None, override=False),
        ]

        voltage = get_val(self.raw_meta, base + ('Voltage',), float)
        if voltage is not None:
            mapping += [
                MappingElements(
                    source_dict=self.raw_meta, dest_dict=dest_dict,
                    source_path=base + ('Voltage',), cast_fn=float,
                    dest_path=('General_EM', 'accelerating_voltage'),
                    units='KiloV' if voltage >= 1000 else 'V',
                    conv_fn=lambda x: x / 1000 if voltage >= 1000 else x, override=False)
            ]

        # "Session Info"
        base = self.__get_dm3_tag_pre_path() + ('Session Info',)
        mapping += [
            MappingElements(
                source_dict=self.raw_meta, source_path=base + ('Detector',),
                dest_dict=dest_dict, dest_path=('General_EM', 'detector_name'),
                cast_fn=str, units=None, conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=base + ('Microscope',),
                dest_dict=dest_dict, dest_path=('General_EM', 'microscope_name'),
                cast_fn=str, units=None, conv_fn=None, override=False)]

        # "Meta Data"
        base = self.__get_dm3_tag_pre_path() + ('Meta Data',)
        mapping += [
            MappingElements(
                source_dict=self.raw_meta, source_path=base + ('Acquisition Mode',),
                dest_dict=dest_dict, dest_path=('TEM', 'acquisition_mode'),
                cast_fn=str, units=None, conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=base + ('Format',),
                dest_dict=dest_dict, dest_path=('TEM', 'acquisition_format'),
                cast_fn=str, units=None, conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=base + ('Signal',),
                dest_dict=dest_dict, dest_path=('TEM', 'acquisition_signal'),
                cast_fn=str, units=None, conv_fn=None, override=False),
            # sometimes the EDS signal label is in a different place
            MappingElements(
                source_dict=self.raw_meta,
                source_path=base + ('Experiment keywords', 'TagGroup1', 'Label'),
                dest_dict=dest_dict, dest_path=('TEM', 'acquisition_signal'),
                cast_fn=str, units=None, conv_fn=None, override=False)
        ]

        # a few miscellaneous DM tags:
        base = self.__get_dm3_tag_pre_path()
        mapping += [
            MappingElements(
                source_dict=self.raw_meta, source_path=base + ('Acquisition', 'Device', 'Name'),
                dest_dict=dest_dict, dest_path=('TEM', 'acquisition_device'),
                cast_fn=str, units=None, conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=base + ('DataBar', 'Device Name'),
                dest_dict=dest_dict, dest_path=('TEM', 'acquisition_device'),
                cast_fn=str, units=None, conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta,
                source_path=base + ('Acquisition', 'Parameters', 'High Level', 'Exposure (s)'),
                dest_dict=dest_dict, dest_path=('General_EM', 'exposure_time'),
                cast_fn=float, units='SEC', conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=base + ('DataBar', 'Exposure Time (s)'),
                dest_dict=dest_dict, dest_path=('General_EM', 'exposure_time'),
                cast_fn=float, units='SEC', conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=base + ('GMS Version', 'Created'),
                dest_dict=dest_dict, dest_path=('General_EM', 'acquisition_software_version'),
                cast_fn=str, units=None, conv_fn=None, override=False)
        ]

        if get_val(self.raw_meta, ('ImageList', 'TagGroup0', 'ImageTags')) is not None:
            # we have DigitalMicrograph tags, so set acquisition software name
            set_val_units(nest_dict=dest_dict, path=('General_EM', 'acquisition_software_name'),
                          value='DigitalMicrograph')

        map_dict_values(mapping)

    def __get_dm3_tag_pre_path(self) -> Tuple:
        """Get the path into a dictionary where the important DigitalMicrograph metadata is
        expected to be found. If the .dm3/.dm4 file contains a stack of images, the metadata to
        extract is instead under a `plane info` tag, so this method will determine if the stack
        metadata is present and return the correct path. ``pre_path`` will be something
        like ``('ImageList', 'TagGroup0', 'ImageTags', 'plane info', 'TagGroup0', 'source tags')``.

        Returns:
            A tuple containing the subsequent keys that need to be traversed to get to the point
            in the ``raw_metadata`` where the important metadata is stored
        """
        # test if we have a stack
        stack_path = ('ImageList', 'TagGroup0', 'ImageTags', 'plane info')
        stack_val = get_val(self.raw_meta, stack_path)
        if stack_val is not None:
            # we're in a stack
            pre_path = ('ImageList', 'TagGroup0', 'ImageTags', 'plane info', 'TagGroup0',
                        'source tags')
        else:
            pre_path = ('ImageList', 'TagGroup0', 'ImageTags')

        return pre_path

    def _dm3_eels_info(self) -> None:
        """Parse EELS-related information from Gatan DigitalMicrograph format
        """
        # basic EELS metadata
        pre_path = self.__get_dm3_tag_pre_path()
        base = pre_path + ('EELS', )
        mapping = [
            MappingElements(
                source_dict=self.raw_meta, dest_dict=self.em,
                source_path=base + ('Acquisition', 'Exposure (s)'),
                dest_path=('General_EM', 'exposure_time'), units='SEC',
                conv_fn=None, cast_fn=float, override=False),
            MappingElements(
                source_dict=self.raw_meta, dest_dict=self.em,
                source_path=base + ('Acquisition', 'Integration time (s)'),
                dest_path=('EELS', 'integration_time'), units='SEC',
                conv_fn=None, cast_fn=float, override=False),
            MappingElements(
                source_dict=self.raw_meta, dest_dict=self.em,
                source_path=base + ('Acquisition', 'Number of frames'),
                dest_path=('EELS', 'number_of_samples'), units='NUM',
                conv_fn=None, cast_fn=int, override=False),
            MappingElements(
                source_dict=self.raw_meta, dest_dict=self.em,
                source_path=base + ('Experimental Conditions', 'Collection semi-angle (mrad)'),
                dest_path=('EELS', 'collection_angle'), units='MilliRAD',
                conv_fn=None, cast_fn=float, override=False),
            MappingElements(
                source_dict=self.raw_meta, dest_dict=self.em,
                source_path=base + ('Experimental Conditions', 'Convergence semi-angle (mrad)'),
                dest_path=('General_EM', 'convergence_angle'), units='MilliRAD',
                conv_fn=None, cast_fn=float, override=False)]

        # spectrometer metadata
        # is usually at one of two places, so try both
        spect_dict = get_val(self.raw_meta, pre_path + ('EELS', 'Acquisition', 'Spectrometer'))
        if spect_dict is not None:
            spect_path = pre_path + ('EELS', 'Acquisition', 'Spectrometer')
        else:
            spect_path = pre_path + ('EELS Spectrometer',)
        mapping += [
            MappingElements(
                source_dict=self.raw_meta, dest_dict=self.em,
                source_path=spect_path + ('Aperture label',),
                dest_path=('EELS', 'aperture_size'), units='MilliM', conv_fn=None,
                cast_fn=lambda s: float(s.replace('mm', '')), override=False),
            MappingElements(
                source_dict=self.raw_meta, dest_dict=self.em,
                source_path=spect_path + ('Dispersion (eV/ch)',),
                dest_path=('EELS', 'dispersion_per_channel'), units='EV', conv_fn=None,
                cast_fn=float, override=False),
            MappingElements(
                source_dict=self.raw_meta, dest_dict=self.em,
                source_path=spect_path + ('Energy loss (eV)',),
                dest_path=('EELS', 'energy_loss_offset'), units='EV', conv_fn=None,
                cast_fn=float, override=False),
            MappingElements(
                source_dict=self.raw_meta, dest_dict=self.em,
                source_path=spect_path + ('Instrument name',),
                dest_path=('EELS', 'spectrometer_name'), units=None, conv_fn=None, cast_fn=str,
                override=False),
            MappingElements(
                source_dict=self.raw_meta, dest_dict=self.em,
                source_path=spect_path + ('Drift tube voltage (V)',),
                dest_path=('EELS', 'drift_tube_voltage'), units='V', conv_fn=None, cast_fn=float,
                override=False),
            MappingElements(
                source_dict=self.raw_meta, dest_dict=self.em,
                source_path=spect_path + ('Drift tube enabled',),
                dest_path=('EELS', 'drift_tube_enabled'), units=None, conv_fn=None, cast_fn=bool,
                override=False),
            MappingElements(
                source_dict=self.raw_meta, dest_dict=self.em,
                source_path=spect_path + ('Prism offset (V)',),
                dest_path=('EELS', 'prism_shift_voltage'), units='V', conv_fn=None,
                cast_fn=float, override=False),
            # note space at end of "Prism offset enabled " because that's how
            # it gets loaded in from DigitalMicrograph...
            MappingElements(
                source_dict=self.raw_meta, dest_dict=self.em,
                source_path=spect_path + ('Prism offset enabled ',),
                dest_path=('EELS', 'prism_shift_enabled'), units=None, conv_fn=None,
                cast_fn=bool, override=False),
            MappingElements(
                source_dict=self.raw_meta, dest_dict=self.em,
                source_path=spect_path + ('Slit width (eV)',),
                dest_path=('EELS', 'filter_slit_width'), units='EV', conv_fn=None, cast_fn=float,
                override=False),
            MappingElements(
                source_dict=self.raw_meta, dest_dict=self.em,
                source_path=spect_path + ('Slit inserted',),
                dest_path=('EELS', 'filter_slit_inserted'), units=None, conv_fn=None,
                cast_fn=bool, override=False),
        ]
        map_dict_values(mapping)

    def _dm3_eds_info(self) -> None:
        """Parse EDS-related information from Gatan DigitalMicrograph format"""
        pre_path = self.__get_dm3_tag_pre_path()
        base = pre_path + ('EDS',)
        mapping = [
            MappingElements(
                source_dict=self.raw_meta, dest_dict=self.em,
                source_path=base + ('Detector Info', 'Azimuthal angle'),
                dest_path=('EDS', 'azimuth_angle'), units='DEG', conv_fn=None, cast_fn=float,
                override=False),
            MappingElements(
                source_dict=self.raw_meta, dest_dict=self.em,
                source_path=base + ('Detector Info', 'Detector type'),
                dest_path=('EDS', 'detector_type'), units=None, conv_fn=None, cast_fn=str,
                override=False),
            MappingElements(
                source_dict=self.raw_meta, dest_dict=self.em,
                source_path=base + ('Acquisition', 'Dispersion (eV)'),
                dest_path=('EDS', 'dispersion_per_channel'), units='EV', conv_fn=None,
                cast_fn=float, override=False),
            MappingElements(
                source_dict=self.raw_meta, dest_dict=self.em,
                source_path=base + ('Detector Info', 'Elevation angle'),
                dest_path=('EDS', 'elevation_angle'), units='DEG', conv_fn=None, cast_fn=float,
                override=False),
            MappingElements(
                source_dict=self.raw_meta, dest_dict=self.em,
                source_path=base + ('Detector Info', 'Incidence angle'),
                dest_path=('EDS', 'incidence_angle'), units='DEG', conv_fn=None, cast_fn=float,
                override=False),
            MappingElements(
                source_dict=self.raw_meta, dest_dict=self.em,
                source_path=base + ('Live time',),
                dest_path=('EDS', 'live_time'), units='SEC', conv_fn=None, cast_fn=float,
                override=False),
            MappingElements(
                source_dict=self.raw_meta, dest_dict=self.em,
                source_path=base + ('Real time',),
                dest_path=('EDS', 'real_time'), units='SEC', conv_fn=None, cast_fn=float,
                override=False),
            MappingElements(
                source_dict=self.raw_meta, dest_dict=self.em,
                source_path=base + ('Detector Info', 'Solid angle'),
                dest_path=('EDS', 'solid_angle'), units='SR', conv_fn=None, cast_fn=float,
                override=False),
            MappingElements(
                source_dict=self.raw_meta, dest_dict=self.em,
                source_path=base + ('Detector Info', 'Stage tilt'),
                dest_path=('EDS', 'stage_tilt'), units='DEG', conv_fn=None, cast_fn=float,
                override=False)
        ]

        map_dict_values(mapping)

    def _dm3_tecnai_info(self, delimiter: Optional[str] = u'\u2028') -> None:
        """Some FEI Microscopes will write additional metadata into dm3 files in a long string
        separated by a unicode delimiter (u'\u2028'), present at
        ``ImageList.TagGroup0.ImageTags.Tecnai.Microscope_Info``. This method parses that
        information.  Adapted from the implementation in https://github.com/usnistgov/NexusLIMS

        args:
            delimiter: The value (a unicode string) used to split the ``microscope_info`` string.
                Should not need to be provided (this value is hard-coded in DigitalMicrograph), but
                specified as a parameter for future flexibility
        """
        def __find_val(s_to_find, list_to_search):
            """Return the first value in ``list_to_search`` that contains ``s_to_find``,
            or ``None`` if it is not found

            Note: If needed, this could be improved to use regex instead, which would provide
            more control over the patterns to return
            """
            res = [x for x in list_to_search if s_to_find in x]
            if len(res) > 0:
                res = res[0]
                # remove the string we searched for from the beginning of
                # the res
                return re.sub("^" + s_to_find, "", res)
            else:
                return None

        def __extract_val(regex: str, str_to_search: str, match_num: int = 1) -> Optional[str]:
            """Extract a value from a string based on a grouped regex
            """
            result = re.compile(regex).search(str_to_search)
            if result is not None:
                result = result[match_num]
            return result

        path_to_tecnai = ('ImageList', 'TagGroup0', 'ImageTags', 'Tecnai', 'Microscope Info')
        self.tecnai_info = get_val(self.raw_meta, path_to_tecnai)

        if self.tecnai_info is None:
            # if tecnai info is not present, return early to save some work
            return
        else:
            # split the tecnai_info string into a list
            self.tecnai_info = self.tecnai_info.split(delimiter)

            # we override existing values since Tecnai info is more specific
            mapping = [
                MappingElements(
                    source_dict={
                        'Microscope_Name': __find_val('Microscope ', self.tecnai_info)},
                    source_path='Microscope_Name', dest_dict=self.em,
                    dest_path=('General_EM', 'microscope_name'), cast_fn=str,
                    units=None, conv_fn=None, override=True),
                MappingElements(
                    source_dict={
                        'Extractor_Voltage':
                            __extract_val(r'Extr volt (\d*) V', __find_val('Extr volt ',
                                                                           self.tecnai_info))},
                    source_path='Extractor_Voltage', dest_dict=self.em,
                    dest_path=('TEM', 'extractor_voltage'), cast_fn=int,
                    units='V', conv_fn=None, override=True),
                MappingElements(
                    source_dict={
                        'Emission_Current':
                            __extract_val(r'Emission ([\d|\.]*)uA', __find_val('Emission ',
                                                                               self.tecnai_info))},
                    source_path='Emission_Current', dest_dict=self.em,
                    dest_path=('General_EM', 'emission_current'), cast_fn=float,
                    units='MicroA', conv_fn=None, override=True),
                MappingElements(
                    source_dict={
                        'Operation_Mode':
                            __extract_val(r'(.*) Defocus', __find_val('Mode ', self.tecnai_info))},
                    source_path='Operation_Mode', dest_dict=self.em,
                    dest_path=('TEM', 'operation_mode'), cast_fn=str,
                    units=None, conv_fn=None, override=True),

                # try two different extractions of defocus for mag mode and
                # diffraction mode:
                MappingElements(
                    source_dict={
                        'Defocus':
                            __extract_val(r'Defocus \(um\) (.*) Magn',
                                          __find_val('Mode ', self.tecnai_info))},
                    source_path='Defocus', dest_dict=self.em,
                    dest_path=('TEM', 'defocus'), cast_fn=float,
                    units='MicroM', conv_fn=None, override=True),
                MappingElements(
                    source_dict={
                        'Defocus':
                            __extract_val(r'Defocus ([\d|\.]*) CL',
                                          __find_val('Mode ', self.tecnai_info))},
                    source_path='Defocus', dest_dict=self.em,
                    dest_path=('TEM', 'defocus'), cast_fn=float,
                    units='MicroM', conv_fn=None, override=True),
                # try magnification (not always present):
                MappingElements(
                    source_dict={
                        'Magnification':
                            __extract_val(r'Magn (\d*)x', __find_val('Mode ', self.tecnai_info))},
                    source_path='Magnification', dest_dict=self.em,
                    dest_path=('General_EM', 'magnification_indicated'),
                    cast_fn=int, units='UNITLESS', conv_fn=None,
                    override=True),
                MappingElements(
                    source_dict={
                        'Camera_Length':
                            __extract_val(r'CL (.*)m', __find_val('Mode ', self.tecnai_info))},
                    source_path='Camera_Length', dest_dict=self.em,
                    dest_path=('TEM', 'camera_length'), cast_fn=float,
                    units='MilliM', conv_fn=lambda x: x*1000, override=True),
                # spot size
                MappingElements(
                    source_dict={'Spot_Size': __find_val('Spot ', self.tecnai_info)},
                    source_path='Spot_Size', dest_dict=self.em,
                    dest_path=('TEM', 'spot_size'), cast_fn=int,
                    units='UNITLESS', conv_fn=None, override=True),
                # Tecnai has info about apertures and lens strengths,
                # but not extracting here (see NexusLIMS code for example)
            ]
            stage_vals = __find_val('Stage', self.tecnai_info)
            if stage_vals:
                x, y, z = re.findall(r' (-?\d*\.\d*) um', stage_vals)
                alpha, beta = re.findall(r' (-?\d*\.\d*) deg', stage_vals)
                stage = {'x': x, 'y': y, 'z': z, 'a': alpha, 'b': beta}
                mapping += [
                    MappingElements(
                        source_dict=stage, source_path='x', dest_dict=self.em,
                        dest_path=('General_EM', 'stage_position', 'x'),
                        cast_fn=float, units='MicroM', conv_fn=None, override=True),
                    MappingElements(
                        source_dict=stage, source_path='y', dest_dict=self.em,
                        dest_path=('General_EM', 'stage_position', 'y'),
                        cast_fn=float, units='MicroM', conv_fn=None, override=True),
                    MappingElements(
                        source_dict=stage, source_path='z', dest_dict=self.em,
                        dest_path=('General_EM', 'stage_position', 'z'),
                        cast_fn=float, units='MicroM', conv_fn=None, override=True),
                    MappingElements(
                        source_dict=stage, source_path='a', dest_dict=self.em,
                        dest_path=('General_EM', 'stage_position', 'tilt_alpha'),
                        cast_fn=float, units='DEG', conv_fn=None, override=True),
                    MappingElements(
                        source_dict=stage, source_path='b', dest_dict=self.em,
                        dest_path=('General_EM', 'stage_position', 'tilt_beta'),
                        cast_fn=float, units='DEG', conv_fn=None, override=True),
                ]

            # process EELS spectrometer info from Tecnai string
            if __find_val('Filter related settings', self.tecnai_info):
                filter_dict = {
                    'Mode': __find_val('Mode: ', self.tecnai_info),
                    'Dispersion': __extract_val(r'(.*)\[eV/Channel\]',
                                                __find_val('Selected dispersion: ',
                                                           self.tecnai_info)),
                    'Aperture': __extract_val(r'(\d*)mm',
                                              __find_val('Selected aperture: ',
                                                         self.tecnai_info)),
                    'Prism': __extract_val(r'(.*)\[eV\]',
                                           __find_val('Prism shift: ', self.tecnai_info)),
                    'Drift': __extract_val(r'(.*)\[eV\]',
                                           __find_val('Drift tube: ', self.tecnai_info)),
                    'TotalLoss': __extract_val(r'(.*)\[eV\]',
                                               __find_val('Total energy loss: ', self.tecnai_info))
                }
                mapping += [
                    MappingElements(
                        source_dict=filter_dict, source_path='Mode',
                        dest_dict=self.em, dest_path=('EELS', 'spectrometer_mode'),
                        cast_fn=str, units=None, conv_fn=None, override=True),
                    MappingElements(
                        source_dict=filter_dict, source_path='Dispersion',
                        dest_dict=self.em, dest_path=('EELS', 'dispersion_per_channel'),
                        cast_fn=float, units='EV', conv_fn=None, override=True),
                    MappingElements(
                        source_dict=filter_dict, source_path='Aperture',
                        dest_dict=self.em, dest_path=('EELS', 'aperture_size'),
                        cast_fn=float, units='MilliM', conv_fn=None, override=True),
                    MappingElements(
                        source_dict=filter_dict, source_path='Drift',
                        dest_dict=self.em, dest_path=('EELS', 'drift_tube_energy'),
                        cast_fn=float, units='EV', conv_fn=None, override=True),
                    MappingElements(
                        source_dict=filter_dict, source_path='Prism',
                        dest_dict=self.em, dest_path=('EELS', 'prism_shift_energy'),
                        cast_fn=float, units='EV', conv_fn=None, override=True),
                    MappingElements(
                        source_dict=filter_dict, source_path='TotalLoss',
                        dest_dict=self.em, dest_path=('EELS', 'total_energy_loss'),
                        cast_fn=float, units='EV', conv_fn=None, override=True),
                ]

            map_dict_values(mapping)

    def _tia_info(self) -> None:
        """Parses information commonly found in .ser/.emi files produced by the "Tecnai Imaging
        and Analysis" (TIA) software

        Terms such as ``IntegrationTime`` and ``EnergyResolution`` appear to be non-specific as
        to acquisition modality (i.e. could be EELS or EDS), so we do not extract those into our
        metadata hierarchy
        """

        mapping = [
            MappingElements(
                source_dict=self.raw_meta,
                source_path=('ObjectInfo', 'ExperimentalConditions',
                             'MicroscopeConditions', 'AcceleratingVoltage'),
                dest_dict=self.em, dest_path=('General_EM', 'accelerating_voltage'),
                cast_fn=float, units='V', conv_fn=None, override=False),

            MappingElements(
                source_dict=self.raw_meta,
                source_path=('ObjectInfo', 'AcquireInfo', 'DwellTimePath'),
                dest_dict=self.em, dest_path=('General_EM', 'dwell_time'),
                cast_fn=float, units='SEC', conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta,
                source_path=('ObjectInfo', 'AcquireInfo', 'FrameTime'),
                dest_dict=self.em, dest_path=('General_EM', 'frame_time'),
                cast_fn=float, units='SEC', conv_fn=None, override=False),

            MappingElements(
                source_dict=self.raw_meta,
                source_path=('ObjectInfo', 'ExperimentalDescription', 'Microscope'),
                dest_dict=self.em, dest_path=('General_EM', 'microscope_name'),
                cast_fn=str, units=None, conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta,
                source_path=('ObjectInfo', 'ExperimentalDescription', 'High tension_kV'),
                dest_dict=self.em, dest_path=('General_EM',
                                              'accelerating_voltage'),
                cast_fn=float, units='KiloV', conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta,
                source_path=('ObjectInfo', 'ExperimentalDescription', 'Emission_uA'),
                dest_dict=self.em, dest_path=('General_EM', 'emission_current'),
                cast_fn=float, units='MicroA', conv_fn=None, override=False),
            # this value is often more specific than the one from HyperSpy,
            # so override acquisition mode:
            MappingElements(
                source_dict=self.raw_meta,
                source_path=('ObjectInfo', 'ExperimentalDescription', 'Mode'),
                dest_dict=self.em, dest_path=('General_EM', 'acquisition_mode'),
                cast_fn=str, units=None, conv_fn=lambda x: x.strip(), override=True),
            MappingElements(
                source_dict=self.raw_meta,
                source_path=('ObjectInfo', 'ExperimentalDescription', 'Defocus_um'),
                dest_dict=self.em, dest_path=('TEM', 'defocus'),
                cast_fn=float, units='MicroM', conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta,
                source_path=('ObjectInfo', 'ExperimentalDescription', 'Magnification_x'),
                dest_dict=self.em, dest_path=('General_EM', 'magnification_indicated'),
                cast_fn=float, units='UNITLESS', conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta,
                source_path=('ObjectInfo', 'ExperimentalDescription', 'Camera length_m'),
                dest_dict=self.em, dest_path=('TEM', 'camera_length'),
                cast_fn=float, units='M', conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta,
                source_path=('ObjectInfo', 'ExperimentalDescription', 'Spot size'),
                dest_dict=self.em, dest_path=('TEM', 'spot_size'),
                cast_fn=int, units='UNITLESS', conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta,
                source_path=('ObjectInfo', 'ExperimentalDescription', 'Stage X_um'),
                dest_dict=self.em, dest_path=('General_EM', 'stage_position', 'x'),
                cast_fn=float, units='MicroM', conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta,
                source_path=('ObjectInfo', 'ExperimentalDescription', 'Stage Y_um'),
                dest_dict=self.em, dest_path=('General_EM', 'stage_position', 'y'),
                cast_fn=float, units='MicroM', conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta,
                source_path=('ObjectInfo', 'ExperimentalDescription', 'Stage Z_um'),
                dest_dict=self.em, dest_path=('General_EM', 'stage_position', 'z'),
                cast_fn=float, units='MicroM', conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta,
                source_path=('ObjectInfo', 'ExperimentalDescription', 'Stage A_deg'),
                dest_dict=self.em, dest_path=('General_EM', 'stage_position', 'tilt_alpha'),
                cast_fn=float, units='DEG', conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta,
                source_path=('ObjectInfo', 'ExperimentalDescription', 'Stage B_deg'),
                dest_dict=self.em, dest_path=('General_EM', 'stage_position', 'tilt_beta'),
                cast_fn=float, units='DEG', conv_fn=None, override=False),

            MappingElements(
                source_dict=self.raw_meta,
                source_path=('ObjectInfo', 'ExperimentalDescription', 'Filter mode'),
                dest_dict=self.em, dest_path=('EELS', 'spectrometer_mode'),
                cast_fn=str, units=None, conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta,
                source_path=('ObjectInfo', 'ExperimentalDescription',
                             'Filter selected dispersion_eV/Channel'),
                dest_dict=self.em, dest_path=('EELS', 'dispersion_per_channel'),
                cast_fn=float, units='EV', conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta,
                source_path=('ObjectInfo', 'ExperimentalDescription', 'Filter selected aperture'),
                dest_dict=self.em, dest_path=('EELS', 'aperture_size'),
                cast_fn=lambda x: float(x.replace('mm', '')), units='MilliM', conv_fn=None,
                override=False),
            MappingElements(
                source_dict=self.raw_meta,
                source_path=('ObjectInfo', 'ExperimentalDescription', 'Filter prism shift_eV'),
                dest_dict=self.em, dest_path=('EELS', 'prism_shift_energy'),
                cast_fn=float, units='EV', conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta,
                source_path=('ObjectInfo', 'ExperimentalDescription', 'Filter drift tube_eV'),
                dest_dict=self.em, dest_path=('EELS', 'drift_tube_energy'),
                cast_fn=float, units='EV', conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta,
                source_path=('ObjectInfo', 'ExperimentalDescription',
                             'Filter total energy loss_eV'),
                dest_dict=self.em, dest_path=('EELS', 'total_energy_loss'),
                cast_fn=float, units='EV', conv_fn=None, override=False)
        ]
        map_dict_values(mapping)

    def _tiff_info(self) -> None:
        """Parses metadata found in FEI/ThermoFisher tiff formats (and perhaps others in the
        future), produced by SEM and dual beam tools
        """
        mapping = [
            MappingElements(
                source_dict=self.raw_meta, source_path=('fei_metadata', 'System', 'Software'),
                dest_dict=self.em, dest_path=('General_EM', 'acquisition_software_version'),
                cast_fn=str, units=None, conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=('fei_metadata', 'Beam', 'Spot'),
                dest_dict=self.em, dest_path=('SEM', 'spot_size'),
                cast_fn=lambda x: int(x) if x != '' else None, units=None, conv_fn=None,
                override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=('fei_metadata', 'Beam', 'HV'),
                dest_dict=self.em, dest_path=('General_EM', 'accelerating_voltage'),
                cast_fn=lambda x: float(x) if x != '' else None, units='KiloV',
                conv_fn=lambda x: x/1000 if x != '' else None, override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=('fei_metadata', 'EBeam', 'HV'),
                dest_dict=self.em, dest_path=('General_EM', 'accelerating_voltage'),
                cast_fn=lambda x: float(x) if x != '' else None,
                units='KiloV', conv_fn=lambda x: x / 1000 if x != '' else None,
                override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=('fei_metadata', 'EBeam', 'HFW'),
                dest_dict=self.em, dest_path=('SEM', 'horizontal_field_width'),
                cast_fn=lambda x: float(x) if x != '' else None, units='M', conv_fn=None,
                override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=('fei_metadata', 'EBeam', 'VFW'),
                dest_dict=self.em, dest_path=('SEM', 'vertical_field_width'),
                cast_fn=lambda x: float(x) if x != '' else None, units='M', conv_fn=None,
                override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=('fei_metadata', 'EBeam', 'WD'),
                dest_dict=self.em, dest_path=('SEM', 'working_distance'),
                cast_fn=lambda x: float(x) if x != '' else None, units='M', conv_fn=None,
                override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=('fei_metadata', 'EBeam', 'BeamCurrent'),
                dest_dict=self.em, dest_path=('General_EM', 'beam_current'),
                cast_fn=lambda x: float(x) if x != '' else None, units='A', conv_fn=None,
                override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=('fei_metadata', 'Stage', 'StageX'),
                dest_dict=self.em, dest_path=('General_EM', 'stage_position', 'x'),
                cast_fn=lambda x: float(x) if x != '' else None, units='MilliM',
                conv_fn=lambda x: x * 1000 if x != '' else None, override=True),
            MappingElements(
                source_dict=self.raw_meta, source_path=('fei_metadata', 'Stage', 'StageY'),
                dest_dict=self.em, dest_path=('General_EM', 'stage_position', 'y'),
                cast_fn=lambda x: float(x) if x != '' else None, units='MilliM',
                conv_fn=lambda x: x * 1000 if x != '' else None, override=True),
            MappingElements(
                source_dict=self.raw_meta, source_path=('fei_metadata', 'Stage', 'StageZ'),
                dest_dict=self.em, dest_path=('General_EM', 'stage_position', 'z'),
                cast_fn=lambda x: float(x) if x != '' else None, units='MilliM',
                conv_fn=lambda x: x * 1000 if x != '' else None, override=True),
            MappingElements(
                source_dict=self.raw_meta, source_path=('fei_metadata', 'Stage', 'StageR'),
                dest_dict=self.em, dest_path=('General_EM', 'stage_position', 'rotation'),
                cast_fn=lambda x: float(x) if x != '' else None, units='DEG', conv_fn=None,
                override=True),
            MappingElements(
                source_dict=self.raw_meta, source_path=('fei_metadata', 'Stage', 'StageT'),
                dest_dict=self.em, dest_path=('General_EM', 'stage_position', 'tilt_alpha'),
                cast_fn=lambda x: float(x) if x != '' else None, units='DEG', conv_fn=None,
                override=True),
            MappingElements(
                source_dict=self.raw_meta, source_path=('fei_metadata', 'Stage', 'StageTb'),
                dest_dict=self.em, dest_path=('General_EM', 'stage_position', 'tilt_beta'),
                cast_fn=lambda x: float(x) if x != '' else None, units='DEG', conv_fn=None,
                override=True),

            MappingElements(
                source_dict=self.raw_meta, source_path=('fei_metadata', 'Scan', 'PixelWidth'),
                dest_dict=self.em, dest_path=('SEM', 'pixel_width'),
                cast_fn=lambda x: float(x) if x != '' else None, units='M', conv_fn=None,
                override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=('fei_metadata', 'Scan', 'PixelHeight'),
                dest_dict=self.em, dest_path=('SEM', 'pixel_height'),
                cast_fn=lambda x: float(x) if x != '' else None, units='M', conv_fn=None,
                override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=('fei_metadata', 'Scan', 'HorFieldsize'),
                dest_dict=self.em, dest_path=('SEM', 'horizontal_field_width'),
                cast_fn=lambda x: float(x) if x != '' else None,
                units='M', conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=('fei_metadata', 'Scan', 'VerFieldsize'),
                dest_dict=self.em, dest_path=('SEM', 'vertical_field_width'),
                cast_fn=lambda x: float(x) if x != '' else None,
                units='M', conv_fn=None, override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=('fei_metadata', 'Scan', 'FrameTime'),
                dest_dict=self.em, dest_path=('General_EM', 'frame_time'),
                cast_fn=lambda x: float(x) if x else None, units='SEC', conv_fn=None,
                override=False),
            MappingElements(
                source_dict=self.raw_meta, source_path=('fei_metadata', 'Image',
                                                        'MagnificationMode'),
                dest_dict=self.em, dest_path=('SEM', 'magnification_mode'),
                cast_fn=None, units=None, conv_fn=None, override=False),
            # confirmed in Quanta SEM manual that the pressure units are Pascals
            MappingElements(
                source_dict=self.raw_meta, source_path=('fei_metadata', 'Vacuum', 'ChPressure'),
                dest_dict=self.em, dest_path=('SEM', 'chamber_pressure'),
                cast_fn=lambda x: float(x) if x else None, units='PA', conv_fn=None, override=False)
        ]
        map_dict_values(mapping)

    def implementors(self):
        return ['Jonathon Gaff <jgaff@uchicago.edu>',
                'Joshua Taillon <joshua.taillon@nist.gov>']

    def version(self):
        return '0.1.2'

    @property
    def schema(self) -> dict:
        """Schema for the output of the parser"""
        with open(pathlib.Path(__file__).parent / 'schemas' /
                  'electron_microscopy.json') as f:
            return json.load(f)
