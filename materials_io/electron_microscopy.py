import hyperspy.api as hs

from materials_io.base import BaseSingleFileParser


class ElectronMicroscopyParser(BaseSingleFileParser):
    """Parse metadata specific to electron microscopy"""

    def _parse_file(self, file_path, context=None):
        # Read file, both HyperSpy-formatted and raw data
        hs_data = hs.load(file_path)
        data = hs_data.metadata.as_dictionary()
        raw_data = hs_data.original_metadata.as_dictionary()

        em = {}
        image = {}
        # Image mode is SEM, TEM, or STEM
        # STEM is a subset of TEM
        if "SEM" in data.get('Acquisition_instrument', {}).keys():
            inst = "SEM"
        elif "TEM" in data.get('Acquisition_instrument', {}).keys():
            inst = "TEM"
        else:
            inst = "None"

        # HS data
        try:
            inst_data = data['Acquisition_instrument'][inst]
        except KeyError:
            pass
        else:
            try:
                em['beam_energy'] = inst_data['beam_energy']
            except KeyError:
                pass
            try:
                em['magnification'] = inst_data['magnification']
            except KeyError:
                pass
            try:
                em['acquisition_mode'] = inst_data['acquisition_mode']
            except KeyError:
                pass
            try:
                detector = inst_data['Detector']
            except KeyError:
                pass
            else:
                em['detector'] = next(iter(detector))

        # Non-HS data (not pulled into standard HS metadata)
        # Pull out common dicts
        try:
            micro_info = raw_data["ImageList"]["TagGroup0"]["ImageTags"]["Microscope Info"]
        except KeyError:
            micro_info = {}
        try:
            exp_desc = raw_data["ObjectInfo"]["ExperimentalDescription"]
        except KeyError:
            exp_desc = {}

        # emission_current
        try:
            em["emission_current"] = micro_info["Emission Current (µA)"]
        except KeyError:
            try:
                em["emission_current"] = exp_desc["Emission_uA"]
            except KeyError:
                pass
        # operation_mode
        try:
            em["operation_mode"] = micro_info["Operation Mode"]
        except KeyError:
            pass
        # microscope
        try:
            em["microscope"] = (raw_data["ImageList"]["TagGroup0"]["ImageTags"]
                                        ["Session Info"]["Microscope"])
        except KeyError:
            try:
                em["microscope"] = micro_info["Name"]
            except KeyError:
                pass
        # spot_size
        try:
            em["spot_size"] = exp_desc["Spot size"]
        except KeyError:
            pass

        # Image metadata
        try:
            shape = []
            base_shape = list(raw_data["ImageList"]["TagGroup0"]
                                      ["ImageData"]["Dimensions"].values())
            # Reverse X and Y order to match MDF schema (y, x, z, ..., channels)
            if len(base_shape) >= 2:
                shape.append(base_shape[1])
                shape.append(base_shape[0])
                shape.extend(base_shape[2:])
            # If 1 dimension, don't need to swap
            elif len(base_shape) > 0:
                shape = base_shape

            if shape:
                image["shape"] = shape
        except KeyError:
            pass

        # Remove None/empty values
        for key, val in list(em.items()):
            if val is None or val == [] or val == {}:
                em.pop(key)

        record = {}
        if em:
            record["electron_microscopy"] = em
        if image:
            record["image"] = image

        return record

    def implementors(self):
        return ['Jonathon Gaff']

    def version(self):
        return '0.0.2'
