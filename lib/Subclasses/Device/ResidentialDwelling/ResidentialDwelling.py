# this device represents the consumption of a given number of dwellings, gathering them into 1 single device.
from typing import Dict

from src.common.DeviceMainClasses import NonControllableDevice


class ResidentialDwelling(NonControllableDevice):

    def __init__(self, name, contracts, agent, aggregators, profiles, parameters=None, filename="lib/Subclasses/Device/ResidentialDwelling/ResidentialDwelling.json"):
        self._number = parameters["number"]  # the number of dwellings represented by this device
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        super()._read_data_profiles(profiles)
        for nature_name in self._technical_profile:
            for i in range(len(self._technical_profile[nature_name])):
                self._technical_profile[nature_name][i] *= self._number

    def description(self, nature_name: str) -> Dict:
        return {"type": "ResidentialDwelling",
                "technical_profile": self._technical_profile[nature_name],
                "moment": self._moment,
                }





