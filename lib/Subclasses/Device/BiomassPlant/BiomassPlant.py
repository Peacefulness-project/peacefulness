# device representing a photovoltaic panel
from src.common.DeviceMainClasses import NonControllableDevice


class BiomassPlant(NonControllableDevice):

    def __init__(self, name, contracts, agent, aggregators, profiles, parameters, filename="lib/Subclasses/Device/BiomassPlant/BiomassPlant.json"):
        time_step = self._catalog.get("time_step")
        self._max_power = parameters["max_power"] * time_step  # max power

        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)

        self._catalog.add(f"{self.name}.exergy_in", 0)
        self._catalog.add(f"{self.name}.exergy_out", 0)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._technical_profile = dict()
        self._efficiency = None

        # usage profile
        self._technical_profile[data_device["usage_profile"]["nature"]] = None

        self._unused_nature_removal()

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        message = {element: self._messages["bottom-up"][element] for element in self._messages["bottom-up"]}
        energy_wanted = {nature.name: message for nature in self.natures}  # consumption which will be asked eventually

        for nature in energy_wanted:
            energy_wanted[nature]["energy_minimum"] = 0  # energy produced by the device
            energy_wanted[nature]["energy_nominal"] = 0  # energy produced by the device
            energy_wanted[nature]["energy_maximum"] = - self._max_power  # energy produced by the device
            # the value is negative because it is produced

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

        # # exergy calculation
        # reference_temperature = self._catalog.get(f"{self._outdoor_temperature_location}.reference_temperature")
        #
        # exergy_in = list()
        # for nature in energy_wanted:
        #     exergy_in.append(energy_received * (1 - reference_temperature/self._fluid_temperature))
        # exergy_in = sum(exergy_in)
        #
        # exergy_out = exergy_in * efficiency
        #
        # self._catalog.set(f"{self.name}.exergy_in", exergy_in)
        # self._catalog.set(f"{self.name}.exergy_out", exergy_out)



