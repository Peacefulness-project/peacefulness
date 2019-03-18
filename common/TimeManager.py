# This class is in charge of time management. It contains the real value of an iteration step and the last
# step of the simulation


class TimeManager:

    def __init__(self, timestep_value=3600, time_limit=24):
        self._start_date = 0  # will be defined later
        self._timestep_value = timestep_value  # value of the timestep used during the simulation (in seconds)
        self._time_limit = time_limit  # latest time step of the simulation (in number of iterations)
        self._catalog = None

    def update_time(self):

        current_time = self._catalog.get("simulation_time")

        physical_time = self._catalog.get("physical_time") + self._timestep_value  # new value of physical time
        self._catalog.set("physical_time", physical_time)  # updating the value of physical time
        self._catalog.set("simulation_time", current_time + 1)

    def add_catalog(self, catalog):
        self._catalog = catalog
        self._catalog.add("physical_time", self._start_date)  # physical time in seconds
        self._catalog.add("simulation_time", 0)  # simulation time in iterations
