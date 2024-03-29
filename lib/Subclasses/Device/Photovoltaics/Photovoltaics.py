# device representing a photovoltaic panel
from typing import Dict

from src.common.DeviceMainClasses import NonControllableDevice


class Photovoltaics(NonControllableDevice):

    def __init__(self, name, contracts, agent, aggregators, profiles, parameters, filename="lib/Subclasses/Device/Photovoltaics/Photovoltaics.json"):
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)

        self._panels = parameters["panels"]

        irradiation_daemon = self._catalog.daemons[parameters["irradiation_daemon"]]
        self._location = irradiation_daemon.location  # the location of the device, in relation with the meteorological data

        # creation of keys for exergy
        self._catalog.add(f"{self.name}_exergy_in", 0)
        self._catalog.add(f"{self.name}_exergy_out", 0)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._technical_profile = dict()

        # usage profile
        self._technical_profile[data_device["usage_profile"]["nature"]] = None

        # efficiency
        self._efficiency = data_device["usage_profile"]["efficiency"]

        # panels surface
        self._surface_panel = data_device["usage_profile"]["surface_panel"]

        self._unused_nature_removal()

    def description(self, nature_name: str) -> Dict:
        return {"type": "PV",
                "surface": self._surface_panel * self._panels,
                "location": self._location,
                "efficiency": self._efficiency,
                }

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually

        irradiation = self._catalog.get(f"{self._location}.total_irradiation_value")

        energy_received = self._surface_panel * self._panels * irradiation / 1000  # as irradiation is in W, it is transformed in kW

        for nature in energy_wanted:
            energy_wanted[nature]["energy_minimum"] = - energy_received * self._efficiency  # energy produced by the device
            energy_wanted[nature]["energy_nominal"] = - energy_received * self._efficiency  # energy produced by the device
            energy_wanted[nature]["energy_maximum"] = - energy_received * self._efficiency  # energy produced by the device
            # the value is negative because it is produced

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

        exergy_in = list()
        for nature in energy_wanted:
            exergy_in.append(energy_received)
        exergy_in = sum(exergy_in)

        exergy_out = exergy_in * self._efficiency

        self._catalog.set(f"{self.name}_exergy_in", exergy_in)
        self._catalog.set(f"{self.name}_exergy_out", exergy_out)






