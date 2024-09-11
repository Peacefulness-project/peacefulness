# this daemon class is designed to serve as a basis for creating daemons aimed at reading data.
import gc

from ijson import items
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

from src.common.Daemon import Daemon, DaemonException
from src.tools.ReadingFunctions import reading_functions


class DataReadingDaemon(Daemon):
    def __init__(self, name: str, period: int, parameters: Dict, filename: str):
        self._location = parameters["location"]  # the location corresponding to the data

        name += "." + self._location
        super().__init__(name, period, parameters, filename)

        # getting the data for the chosen location
        with open(filename, "r") as file:
            temp = items(file, f"{self._location}", use_float=True)  # the data corresponding to the specified location
            for truc in temp:
                self._data = truc

        self._format = self._data["format"]
        self._get_data = reading_functions[self._format]  # the format acts a tag returning the relevant reading function

        self._managed_keys: List[Tuple] = []  # a list of tuple of keys managed by each daemon. The format is the following:
        # ("key_name_in_data", "key_name_in_catalog", "intensive" OR "extensive")

        # to consult this daemon data easily
        # it is designed for a forecasting use
        def consult_data(depth: int) -> Dict:
            """
            A method specific to each data-based daemons enabling them to give information on several time steps on demand.

            Parameters
            ----------
            depth: int, the number of consecutive time steps consulted from the current one

            Returns
            -------
            A dict on the "key": [data] format

            """
            consulted_data = {key_tuple[1]: [] for key_tuple in self.managed_keys}
            for i in range(depth):
                one_time_step_data = self._data_update(1, i)
                for catalog_key, value in one_time_step_data:
                    consulted_data[catalog_key].append(value)

            return consulted_data
        self._catalog.add(f"consult_function.{type(self).__name__}.{self.location}", consult_data)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _initialize_managed_keys(self):
        value_dict = self._data_update(self._period, 0)
        for data_key, catalog_key, quantity_type in self.managed_keys:
            value = value_dict[catalog_key]
            self.catalog.add(catalog_key, value)

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _process(self):
        values_dict = self._data_update(self.period, 0)

        for catalog_key in values_dict:
            self.catalog.set(catalog_key, values_dict[catalog_key])

    def _data_update(self, time_step_length: int, offset_bis: int):
        """
        For this kind of daemon, the process consists in updating a value in the catalog according to their own data dictionary.
        Their main job is to handle time steps different from 1 hour.
        /!\ here, it is assumed that an arithmetic mean and a simple sum are the good ways to manage respectively intensive and extensive quantities.

        Returns
        -------
        None, the values are directly updated in the catalog
        """
        time_step_value = self._catalog.get("time_step")

        # relevant datetime identification
        real_physical_time_start = self.catalog.get("physical_time") + timedelta(hours=time_step_value * offset_bis)

        # ##########################################################################################
        # start management
        rounded_physical_time_start = datetime(
            year=real_physical_time_start.year,
            month=real_physical_time_start.month,
            day=real_physical_time_start.day,
            hour=real_physical_time_start.hour
        )  # datetime rounded to the hour, for coherence with data format
        first_hour_fraction = 1 - (real_physical_time_start - rounded_physical_time_start).days / 24

        # ##########################################################################################
        # end management
        real_physical_time_end = real_physical_time_start + timedelta(hours=time_step_value * time_step_length)
        rounded_physical_time_end = datetime(
            year=real_physical_time_end.year,
            month=real_physical_time_end.month,
            day=real_physical_time_end.day,
            hour=real_physical_time_end.hour
        )  # datetime rounded to the hour, for coherence with data format
        last_hour_fraction = (real_physical_time_end - rounded_physical_time_end).days / 24

        # start date
        needed_hours = list()  # relevant hours to read, with a coefficient for the first and last hours
        needed_hours.append((0, first_hour_fraction))  # first hour management

        # central hours
        time = rounded_physical_time_start + timedelta(hours=1)
        offset = 1
        while (time - rounded_physical_time_end).days > 0:  # while the last hour is not reached
            needed_hours.append((-offset, 1))
            time += timedelta(hours=1)
            offset += 1

        # end date
        needed_hours.append((-self._period, last_hour_fraction))  # last hour management

        values_dict = {}
        for data_key, catalog_key, quantity_type in self.managed_keys:
            if quantity_type == "extensive":  # ... values are divided if the quantity is extensive
                value = 0
                for i in range(len(needed_hours)):
                    value += self._get_data(self._data[data_key], self.catalog, needed_hours[i][0]) * needed_hours[i][1]
                values_dict[catalog_key] = value
            elif quantity_type == "intensive":  # ... values are the same if the quantity is intensive
                values = []
                coefs = []
                for i in range(len(needed_hours)):
                    values.append(self._get_data(self._data[data_key], self.catalog, needed_hours[i][0]) * needed_hours[i][1])
                    coefs.append(needed_hours[i][1])
                mean_values = sum(values) / sum(coefs)
                values_dict[catalog_key] = mean_values
            else:  # an error is raised otherwise
                raise DaemonException(f"The type of a quantity must be either 'intensive' either 'extensive'.\n"
                                      f"It's not the case for the key {data_key} of daemon {self.name}.")

        return values_dict

    def final_process(self):
        """
        Method used by world to modify a catalog key at the end of a run.
        """
        self._catalog.remove(f"consult_function.{type(self).__name__}.{self.location}")

    # ##########################################################################################
    # Utilities
    # ##########################################################################################

    @property
    def location(self):
        return self._location

    @property
    def data(self):
        return self._data

    @property
    def managed_keys(self):
        return self._managed_keys



