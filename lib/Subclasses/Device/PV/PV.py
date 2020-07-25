# device representing a photovoltaic panel
from src.common.DeviceMainClasses import NonControllableDevice


class PV(NonControllableDevice):

    def __init__(self, name, contracts, agent, aggregators, technical_profile, parameters, filename="lib/Subclasses/Device/PV/PV.json"):
        super().__init__(name, contracts, agent, aggregators, filename, None, technical_profile, parameters)

        self._surface = parameters["surface"]
        self._location = parameters["location"]  # the location of the device, in relation with the meteorological data

        # creation of keys for exergy
        self._catalog.add(f"{self.name}_exergy_in", 0)
        self._catalog.add(f"{self.name}_exergy_out", 0)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, user_profile, technical_profile):
        data_device = self._read_technical_data(technical_profile)  # parsing the data

        self._technical_profile = dict()

        # usage profile
        self._technical_profile[data_device["usage_profile"]["nature"]] = None

        # efficiency
        self._efficiency = data_device["usage_profile"]["efficiency"]

        self._unused_nature_removal()

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        message = {element: self._messages["ascendant"][element] for element in self._messages["ascendant"]}
        energy_wanted = {nature.name: message for nature in self.natures}  # consumption which will be asked eventually

        irradiation = self._catalog.get(f"{self._location}.irradiation_value")

        energy_received = self._surface * irradiation / 1000  # as irradiation is in W, it is transformed in kW

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







