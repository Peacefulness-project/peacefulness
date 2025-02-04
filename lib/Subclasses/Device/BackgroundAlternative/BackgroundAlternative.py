from typing import Dict

from src.common.DeviceMainClasses import NonControllableDevice


class BackgroundAlternative(NonControllableDevice):

    def __init__(self, name, contracts, agent, aggregators, profiles, parameters=None, filename="lib/Subclasses/Device/BackgroundAlternative/BackgroundAlternative.json"):
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        super()._read_data_profiles(profiles)

    def description(self, nature_name: str) -> Dict:
        return {"type": "background",
                "technical_profile": self._technical_profile[nature_name],
                "moment": self._moment,
                }