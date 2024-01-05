# device representing an electric dams
from src.common.DeviceMainClasses import NonControllableDevice


class ElectricDam(NonControllableDevice):

    def __init__(self, name, contracts, agent, aggregators, profiles, parameters, filename="lib/Subclasses/Device/ElectricDam/ElectricDam.json"):
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)

        self._height = parameters["height"]
        time_step = self._catalog.get("time_step")
        self._max_power = parameters["max_power"] * time_step  # max power

        water_flow_daemon = self._catalog.daemons[parameters["water_flow_daemon"]]
        self._location = water_flow_daemon.location  # the location of the device, in relation with the meteorological data

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
        self._max_efficiency = data_device["usage_profile"]["max_efficiency"]

        # relative flow
        self._relative_flow = data_device["usage_profile"]["efficiency"]["relative_flow"]

        # relative efficiency
        self._relative_efficiency = data_device["usage_profile"]["efficiency"]["relative_efficiency"]

        self._relative_min_flow = data_device["usage_profile"]["relative_min_flow"]

        self._unused_nature_removal()

    def description(self, nature_name: str):
        return {"type": "dam",
                "max_power": self._max_power,
                "location": self._location,
                "max_efficiency": self._max_efficiency,
                "relative_efficiency": self._relative_efficiency,
                "relative_min_flow": self._relative_min_flow,
                "height": self._height,
                }

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        water_density = 1000
        reserved_flow = self._catalog.get(f"{self._location}.reserved_flow")
        flow = self._catalog.get(f"{self._location}.flow_value") * (1 - reserved_flow)
        max_flow = self._catalog.get(f"{self._location}.max_flow") * (1 - reserved_flow)

        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually

        # finding the adapted efficiency
        power_available = flow * water_density * self._height * 9.81 / 1000
        i = 0
        while power_available / self._max_power > self._relative_flow[i] and i < len(self._relative_flow)-1:
            i += 1
        coeff_efficiency = self._relative_efficiency[i]

        efficiency = self._max_efficiency * coeff_efficiency

        if flow > self._relative_min_flow * max_flow:
            energy_received = water_density * 9.81 * flow * self._height / 1000  # conversion of water flow, in m3.s-1, to kWh
        else:
            energy_received = 0

        for nature in energy_wanted:
            energy_wanted[nature]["energy_minimum"] = 0  # energy produced by the device
            energy_wanted[nature]["energy_nominal"] = 0  # energy produced by the device
            energy_wanted[nature]["energy_maximum"] = - min(self._max_power, energy_received * efficiency)  # energy produced by the device
            # the value is negative because it is produced

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog








