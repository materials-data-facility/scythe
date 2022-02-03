from hyperspy.io import load as hs_load

from materials_io.base import BaseSingleFileParser
from materials_io.utils import get_nested_dict_value_by_path as get_val
from materials_io.utils import map_dict_values, MappingElements
from materials_io.utils import set_nested_dict_value_with_units as set_val_units

from typing import Tuple, Dict, List


class ElectronMicroscopyParser(BaseSingleFileParser):
    """Parse metadata specific to electron microscopy, meaning any file
    supported by HyperSpy's I/O capabilities. Extract both the metadata
    interpreted by HyperSpy directly, but also any important values we can
    pick out manually.

    For each value (if known), return the subdict:
      {
        "value": numeric/str value,
        "unit": unit name from http://qudt.org/vocab/unit/ (see 
                http://www.qudt.org/doc/DOC_VOCAB-UNITS.html for details)
      }
    
    For base EM, return the following under "General_EM"
      - X accelerating_voltage
      - X acquisition_mode
      - acquisition_software_name
      - acquisition_software_version
      - X beam_current (measured at the sample)
      - X beam_energy 
      - X convergence_angle
      - X detector_name
      - X dwell_time (for STEM modes)
      - emission_current
      - X exposure_time (for non-STEM modes)
      - X elements (list of str - as detected from spectroscopy signal)
      - X magnification_actual
      - X magnification_indicated
      - X microscope_name
      - X probe_area
      - X stage_position (dict with X, Y, Z, R, etc. as required)

    For all, return the following under "General" (if known, from HyperSpy,
      following their metadata definitions:
      http://hyperspy.org/hyperspy-doc/current/user_guide/metadata_structure
      .html)
     - authors : str 
       - The authors of the data, in Latex format: Surname1, Name1 and
         Surname2, Name2, etc.
     - date : str
       - The acquisition or creation date in ISO 8601 date format,
         e.g. ‘2018-01-28’
     - doi : str
       - Digital object identifier of the data, e.g. doi:10.5281/zenodo.58841
     - original_filename : str
       - If the signal was loaded from a file this key stores the name of the
         original file
     - notes : str
       - Notes about the data
     - time : str
       - The acquisition or creation time in ISO 8601 time format,
         e.g. ‘13:29:10’
     - time_zone : str
       - The time zone in either tzdata form, e.g. “UTC”, “America/New_York”,
         etc., or a time offset, e.g. “+03:00” or “-05:00”
     - title : str
       - A title for the signal, e.g. “Sample overview”

    For TEM:
      - acquisition_device
      - X illumination_mode
      - X imaging_mode
      - X operation_mode
      - X spherical_aberration_coefficient
      - defocus
      - spot_size
      - X camera_length

    For SEM:
      - chamber_pressure
      - horizontal_field_width
      - magnification_mode
      - pixel_height
      - pixel_width
      - frame_time
      - working_distance
      - vertical_field_width
      
    For EELS:
      - X aperture_size
      - X collection_angle
      - dispersion_per_channel
      - drift_tube_energy
      - X number_of_samples (The number of frames/spectra integrated during the
                             acquisition.)
      - prism_shift_energy
      - spectrometer_mode
      - X spectrometer_name
      - total_energy_loss

    For EDS:
      - X azimuth_angle
      - X elevation_angle
      - X energy_resolution_MnKa
      - X live_time
      - X real_time
      - dispersion_per_channel

    For all:
      - raw_metadata - the superset of whatever metadata was extracted from
        the original file
    """

    def _parse_file(self, file_path: str, context: Dict = None) -> Dict:
        self.em = {}
        self.image = {}
        self.inst_data = None

        # Read file lazily (reduce memory), both HyperSpy-formatted and raw data
        hs_data = hs_load(file_path, lazy=True)

        # if hs_data is a list, pull out first for metadata extraction
        if isinstance(hs_data, list):
            hs_data = hs_data[0]

        self.meta = hs_data.metadata.as_dictionary()
        self.raw_meta = hs_data.original_metadata.as_dictionary()
        self.em['raw_metadata'] = self.raw_meta

        for s in ['General', 'General_EM', 'TEM', 'SEM', 'EDS', 'EELS']:
            self.em[s] = {}

        # call each individual processor
        self._process_hs_data()
        self._dm3_microscope_info()
        self._dm3_session_info()
        self._dm3_meta_data_info()
        self._dm3_eels_info()
        self._dm3_eds_info()
        self._dm3_spectrum_image_info()
        self._tia_info()  # ...and so on
        self._tiff_info()  # ...and so on

        # Non-HS data (not pulled into standard HS metadata)
        # Pull out common dicts
        try:
            micro_info = self.raw_meta["ImageList"]["TagGroup0"]["ImageTags"][
                "Microscope Info"]
        except Exception:
            micro_info = {}
        try:
            exp_desc = self.raw_meta["ObjectInfo"]["ExperimentalDescription"]
        except Exception:
            exp_desc = {}

        # emission_current
        try:
            self.em["emission_current"] = float(micro_info["Emission Current (µA)"])
        except Exception:
            try:
                self.em["emission_current"] = float(exp_desc["Emission_uA"])
            except Exception:
                pass
        # operation_mode
        try:
            self.em["operation_mode"] = str(micro_info["Operation Mode"])
        except Exception:
            pass
        # microscope
        try:
            self.em["microscope"] = str(self.raw_meta["ImageList"]["TagGroup0"]["ImageTags"]
                                           ["Session Info"]["Microscope"])
        except Exception:
            try:
                self.em["microscope"] = str(micro_info["Name"])
            except Exception:
                pass
        # spot_size
        try:
            self.em["spot_size"] = int(exp_desc["Spot size"])
        except Exception:
            pass

        # Image metadata
        try:
            shape = []
            base_shape = [int(dim) for dim in self.raw_meta["ImageList"]["TagGroup0"]
                                                      ["ImageData"]["Dimensions"].values()]
            # Reverse X and Y order to match MDF schema (y, x, z, ..., channels)
            if len(base_shape) >= 2:
                shape.append(base_shape[1])
                shape.append(base_shape[0])
                shape.extend(base_shape[2:])
            # If 1 dimension, don't need to swap
            elif len(base_shape) > 0:
                shape = base_shape

            if shape:
                self.image["shape"] = shape
        except Exception as e:
            print(e)
            pass

        # Remove None/empty values
        for key, val in list(self.em.items()):
            if val is None or val == [] or val == {}:
                self.em.pop(key)

        record = {}
        if self.em:
            record["electron_microscopy"] = self.em
        if self.image:
            record["image"] = self.image

        return record

    def _process_hs_data(self) -> None:
        # Image mode is SEM, TEM, or STEM
        # STEM is a subset of TEM
        if "SEM" in self.meta.get('Acquisition_instrument', {}).keys():
            self.inst = "SEM"
        elif "TEM" in self.meta.get('Acquisition_instrument', {}).keys():
            self.inst = "TEM"
        else:
            self.inst = 'None'

        # HS data
        self.inst_data = get_val(self.meta, ('Acquisition_instrument',
                                             self.inst))
        if self.inst_data is not None:
            mapping = [
                MappingElements(
                    source_dict=self.inst_data, source_path='acquisition_mode',
                    dest_dict=self.em, dest_path=('General_EM',
                                                  'acquisition_mode'),
                    cast_fn=str, units=None, conv_fn=None),
                MappingElements(
                    source_dict=self.inst_data, source_path='beam_current',
                    dest_dict=self.em, dest_path=('General_EM', 'beam_current'),
                    cast_fn=float, units='NanoA', conv_fn=None),
                MappingElements(
                    source_dict=self.inst_data, source_path='beam_energy',
                    dest_dict=self.em, dest_path=('General_EM', 'beam_energy'),
                    cast_fn=float, units='KiloEV', conv_fn=None),
                MappingElements(
                    source_dict=self.inst_data, source_path='convergence_angle',
                    dest_dict=self.em, dest_path=('General_EM',
                                                  'convergence_angle'),
                    cast_fn=float, units='MilliRAD', conv_fn=None),
                MappingElements(
                    source_dict=self.inst_data, source_path='magnification',
                    dest_dict=self.em, dest_path=('General_EM',
                                                  'magnification_indicated'),
                    cast_fn=float, units='UNITLESS', conv_fn=None),
                MappingElements(
                    source_dict=self.inst_data, source_path='microscope',
                    dest_dict=self.em, dest_path=('General_EM',
                                                  'microscope_name'),
                    cast_fn=str, units=None, conv_fn=None),
                MappingElements(
                    source_dict=self.inst_data, source_path='probe_area',
                    dest_dict=self.em, dest_path=('General_EM', 'probe_area'),
                    cast_fn=float, units='NanoM2', conv_fn=None),

                # stage positions
                MappingElements(
                    source_dict=self.inst_data,
                    source_path=('Stage', 'rotation'),
                    dest_dict=self.em,
                    dest_path=('General_EM', 'stage_position', 'rotation'),
                    cast_fn=float, units='DEG', conv_fn=None),
                MappingElements(
                    source_dict=self.inst_data,
                    source_path=('Stage', 'tilt_alpha'),
                    dest_dict=self.em,
                    dest_path=('General_EM', 'stage_position', 'tilt_alpha'),
                    cast_fn=float, units='DEG', conv_fn=None),
                MappingElements(
                    source_dict=self.inst_data,
                    source_path=('Stage', 'tilt_beta'),
                    dest_dict=self.em,
                    dest_path=('General_EM', 'stage_position', 'tilt_beta'),
                    cast_fn=float, units='DEG', conv_fn=None),
                MappingElements(
                    source_dict=self.inst_data,
                    dest_dict=self.em,
                    source_path=('Stage', 'x'),
                    dest_path=('General_EM', 'stage_position', 'x'),
                    cast_fn=float, units='MilliM', conv_fn=None),
                MappingElements(
                    source_dict=self.inst_data,
                    source_path=('Stage', 'y'),
                    dest_dict=self.em,
                    dest_path=('General_EM', 'stage_position', 'y'),
                    cast_fn=float, units='MilliM', conv_fn=None),
                MappingElements(
                    source_dict=self.inst_data,
                    source_path=('Stage', 'z'),
                    dest_dict=self.em,
                    dest_path=('General_EM', 'stage_position', 'z'),
                    cast_fn=float, units='MilliM', conv_fn=None),

                # camera length/working distance
                MappingElements(
                    source_dict=self.inst_data, source_path='camera_length',
                    dest_dict=self.em, dest_path=('TEM', 'camera_length'),
                    cast_fn=float, units='MilliM', conv_fn=None),
                MappingElements(
                    source_dict=self.inst_data, source_path='working_distance',
                    dest_dict=self.em, dest_path=('SEM', 'working_distance'),
                    cast_fn=float, units='MilliM', conv_fn=None)
            ]

            map_dict_values(mapping)

            self._process_hs_detectors()

        # Elements present (if known)
        set_val_units(self.em, ('General_EM', 'elements'),
                      get_val(self.meta, ('Sample', 'elements'), list))

        # General metadata
        set_val_units(self.em, ('General', 'authors'),
                      get_val(self.meta, ('General', 'authors'), str))
        set_val_units(self.em, ('General', 'date'),
                      get_val(self.meta, ('General', 'date'), str))
        set_val_units(self.em, ('General', 'doi'),
                      get_val(self.meta, ('General', 'doi'), str))
        set_val_units(self.em, ('General', 'original_filename'),
                      get_val(self.meta, ('General', 'original_filename'), str))
        set_val_units(self.em, ('General', 'notes'),
                      get_val(self.meta, ('General', 'notes'), str))
        set_val_units(self.em, ('General', 'time'),
                      get_val(self.meta, ('General', 'time'), str))
        set_val_units(self.em, ('General', 'time_zone'),
                      get_val(self.meta, ('General', 'time_zone'), str))
        set_val_units(self.em, ('General', 'title'),
                      get_val(self.meta, ('General', 'title'), str))

    def _process_hs_detectors(self) -> None:
        """
        Parses HyperSpy-formatted metadata specific to detectors as specified by
        http://hyperspy.org/hyperspy-doc/current/user_guide
        /metadata_structure.html
        """
        detector_node = get_val(self.inst_data, 'Detector')
        mapping = [
            MappingElements(
                source_dict=self.inst_data, source_path='detector_type',
                dest_dict=self.em, dest_path=('General_EM', 'detector_name'),
                cast_fn=str, units=None, conv_fn=None
            )
        ]

        if detector_node is not None:
            mapping += [
                # EDS
                MappingElements(
                    source_dict=detector_node,
                    source_path=('EDS', 'azimuth_angle'),
                    dest_dict=self.em, dest_path=('EDS', 'azimuth_angle'),
                    cast_fn=float, units='DEG', conv_fn=None),
                MappingElements(
                    source_dict=detector_node,
                    source_path=('EDS', 'elevation_angle'),
                    dest_dict=self.em, dest_path=('EDS', 'elevation_angle'),
                    cast_fn=float, units='DEG', conv_fn=None),
                MappingElements(
                    source_dict=detector_node,
                    source_path=('EDS', 'energy_resolution_MnKa'),
                    dest_dict=self.em,
                    dest_path=('EDS', 'energy_resolution_MnKa'),
                    cast_fn=float, units='EV', conv_fn=None),
                MappingElements(
                    source_dict=detector_node, source_path=('EDS', 'live_time'),
                    dest_dict=self.em, dest_path=('EDS', 'live_time'),
                    cast_fn=float, units='SEC', conv_fn=None),
                MappingElements(
                    source_dict=detector_node, source_path=('EDS', 'real_time'),
                    dest_dict=self.em, dest_path=('EDS', 'real_time'),
                    cast_fn=float, units='SEC', conv_fn=None),

                # EELS
                MappingElements(
                    source_dict=detector_node,
                    source_path=('EELS', 'aperture_size'),
                    dest_dict=self.em, dest_path=('EELS', 'aperture_size'),
                    cast_fn=float, units='MilliM', conv_fn=None),
                MappingElements(
                    source_dict=detector_node,
                    source_path=('EELS', 'collection_angle'),
                    dest_dict=self.em, dest_path=('EELS', 'collection_angle'),
                    cast_fn=float, units='MilliRAD', conv_fn=None),
                MappingElements(
                    source_dict=detector_node,
                    source_path=('EELS', 'dwell_time'),
                    dest_dict=self.em, dest_path=('General_EM', 'dwell_time'),
                    cast_fn=float, units='SEC', conv_fn=None),
                MappingElements(
                    source_dict=detector_node,
                    source_path=('EELS', 'exposure'),
                    dest_dict=self.em,
                    dest_path=('General_EM', 'exposure_time'),
                    cast_fn=float, units='SEC', conv_fn=None),
                MappingElements(
                    source_dict=detector_node,
                    source_path=('EELS', 'frame_number'),
                    dest_dict=self.em,
                    dest_path=('EELS', 'number_of_samples'),
                    cast_fn=int, units='NUM', conv_fn=None),
                MappingElements(
                    source_dict=detector_node,
                    source_path=('EELS', 'spectrometer'),
                    dest_dict=self.em,
                    dest_path=('EELS', 'spectrometer_name'),
                    cast_fn=str, units=None, conv_fn=None),
            ]
        map_dict_values(mapping)

    def implementors(self):
        return ['Jonathon Gaff <jgaff@uchicago.edu>',
                'Joshua Taillon <joshua.taillon@nist.gov>']

    def version(self):
        return '0.0.3'


