# this datalogger
from src.common.Datalogger import Datalogger

from src.tools.FilesExtensions import __text_extension__


class PeakToAverageDatalogger(Datalogger):  # a sub-class of dataloggers designed to export values concerning the whole run

    def __init__(self):
        super().__init__("peak_to_average", "peak_to_average", "global")

        natures_list = self._catalog.get("dictionaries")['natures'].keys()  # get all the names

        for nature_name in natures_list:  # for each aggregator registered into world, all the relevant keys are added
            self.add(f"{nature_name}.energy_consumed")
            self.add(f"{nature_name}.energy_produced")

    def final_process(self):
        file = open(self._path + self._filename + __text_extension__, "a+")

        natures_list = self._catalog.get("dictionaries")['natures'].keys()  # get all the names
        for nature_name in natures_list:
            file.write(f"for nature {nature_name}\n")
            if self._buffer[f"{nature_name}.energy_consumed"]["max"] != 0:
                peak_to_average_consumption = self._buffer[f"{nature_name}.energy_consumed"]["mean"] / self._buffer[f"{nature_name}.energy_consumed"]["max"]
            else:
                peak_to_average_consumption = None
            file.write(f"\tpeak-to-average consumption: {peak_to_average_consumption}\n")

            if self._buffer[f"{nature_name}.energy_produced"]["max"] != 0:
                peak_to_average_production = self._buffer[f"{nature_name}.energy_produced"]["mean"] / self._buffer[f"{nature_name}.energy_produced"]["max"]
            else:
                peak_to_average_production = None
            file.write(f"\tpeak-to-average production: {peak_to_average_production}\n")

            file.write("\n")

        file.close()





