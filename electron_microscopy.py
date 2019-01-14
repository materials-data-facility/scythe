import hyperspy.api as hs

from base import BaseParser


class ElectronMicroscopyParser(BaseParser):
    def parse(self, group, context=None):
        records = []
        for file_path in group:
            try:
                data = hs.load(file_path).metadata.as_dictionary()
            except Exception:
                pass
            else:
                em = {}
                # Image mode is SEM, TEM, or STEM.
                # STEM is a subset of TEM.
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
                if em:
                    records.append({
                        "electron_microscopy": em
                    })
        return records
