# This class is in charge of time management. It contains the real value of an iteration step and the last
# step of the simulation
import datetime


class TimeManager:

    def __init__(self, start_date=datetime.datetime.now(), timestep_value=1, time_limit=24):
        self._start_date = start_date  # the format is the following : [minute, hour, day, month, year]
        self._timestep_value = datetime.timedelta(hours=timestep_value)  # value of the timestep used during the
        # simulation (in hours)
        self._time_limit = time_limit  # latest time step of the simulation (in number of iterations)
        self._catalog = None

    def _add_catalog(self, catalog):  # add a catalog
        self._catalog = catalog
        self._catalog.add("physical_time", self._start_date)  # physical time in seconds
        self._catalog.add("simulation_time", 0)  # simulation time in iterations

    def _update_time(self):  # update the time entries in the catalog to the next iteration step

        current_time = self._catalog.get("simulation_time")

        physical_time = self._catalog.get("physical_time")
        physical_time += self._timestep_value  # new value of physical time

        self._catalog.set("physical_time", physical_time)  # updating the value of physical time
        self._catalog.set("simulation_time", current_time + 1)

