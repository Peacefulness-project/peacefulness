# this daemon is designed to manage teh temperature in the system
# Here, it is very basic as it supposes that temperature is uniform and constant
from lib.Subclasses.Daemon.DataReadingDaemon.DataReadingDaemon import DataReadingDaemon


class OutdoorTemperatureDaemon(DataReadingDaemon):

    def __init__(self, parameters, period=1, filename="lib/Subclasses/Daemon/OutdoorTemperatureDaemon/TemperatureProfiles.json", exergy: bool=True):

        name = "outdoor_temperature_in_"
        super().__init__(name, period, parameters, filename)

        self._managed_keys = [("temperatures", f"{self._location}.current_outdoor_temperature", "intensive")]

        self._initialize_managed_keys()

        # previous temperature mangement
        self._data["previous_temperatures"] = []
        physical_time = self._catalog.get("physical_time")
        self._catalog.add(f"{self._location}.previous_outdoor_temperature", self._get_data(self.data["temperatures"], physical_time))  # setting the initial value of previous temperature

        # exergy mangement
        self._exergy = exergy
        if exergy:
            current_month = str(self._catalog.get("physical_time").month)  # the current month in the year
            self._catalog.add(f"{self._location}.reference_temperature", self.data["exergy_reference_temperatures"][current_month])  # reference temperature used for the calculation of exergy

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def _process(self):
        super()._process()

        # previous temperature management
        current_outdoor_temperature = self._catalog.get(f"{self._location}.current_outdoor_temperature")
        self._catalog.set(f"{self._location}.previous_outdoor_temperature", current_outdoor_temperature)  # updating the previous temperature

        # exergy management
        if self._exergy:
            current_month = str(self._catalog.get("physical_time").month)  # the current month in the year
            self._catalog.set(f"{self._location}.reference_temperature", self.data["exergy_reference_temperatures"][current_month])  # reference temperature used for the calculation of exergy



