import hyperspy.api as hs

from materials_io.base import BaseSingleFileParser


class ElectronMicroscopyParser(BaseSingleFileParser):
    """Parse metadata specific to electron microscopy"""

    def _parse_file(self, file_path, context=None):
        data = hs.load(file_path).metadata.as_dictionary()
        em = {}

        # Image mode is SEM, TEM, or STEM.
        #  STEM is a subset of TEM.
        if "SEM" in data.get('Acquisition_instrument', {}).keys():
            inst = "SEM"
        elif "TEM" in data.get('Acquisition_instrument', {}).keys():
            inst = "TEM"
        else:
            inst = "None"
        em['beam_energy'] = (data.get('Acquisition_instrument', {}).get(inst, {})
                                 .get('beam_energy', None))
        em['magnification'] = (data.get('Acquisition_instrument', {}).get(inst, {})
                                   .get('magnification', None))
        em['image_mode'] = (data.get('Acquisition_instrument', {}).get(inst, {})
                                .get('acquisition_mode', None))
        detector = (data.get('Acquisition_instrument', {}).get(inst, {})
                        .get('Detector', None))
        if detector:
            em['detector'] = next(iter(detector))

        # Remove None values
        for key, val in list(em.items()):
            if val is None:
                em.pop(key)

        # Only store record if it has any data
        if em:
            return {'electron_microscopy': em}
        else:
            return {}

    def implementors(self):
        return ['Jonathon Gaff']

    def version(self):
        return '0.0.1'
