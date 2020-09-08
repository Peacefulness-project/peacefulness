# These dataloggers exports the balances for one subclass of device
from src.common.Datalogger import Datalogger
from src.tools.GraphAndTex import __default_graph_options__


class DeviceSubclassBalancesDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, subclass, period=1, graph_options=__default_graph_options__):
        self._devices_list = {}

        if period == "global":
            super().__init__(f"device_{subclass}_balances_global", f"DeviceBalances_{subclass}_global", period)
        else:
            super().__init__(f"device_{subclass}_balances_frequency_{period}", f"DeviceBalances_{subclass}_frequency_{period}", period, graph_options=graph_options, graph_labels={"xlabel": "time", "ylabel": f"{subclass} energy", "y2label": f"{subclass} money"})
            
        def get_quantity(name):
            quantity = 0
            for device_name in self._devices_list.keys():  # for each nature registered into world, all the relevant keys are added
                for nature_name in self._devices_list[device_name]:
                    quantity += self._catalog.get(f"{device_name}.{nature_name}.energy_accorded")["quantity"]

            return quantity

        def get_money(name):
            money = 0
            for device_name in self._devices_list.keys():  # for each nature registered into world, all the relevant keys are added
                for nature_name in self._devices_list[device_name]:
                    energy = self._catalog.get(f"{device_name}.{nature_name}.energy_accorded")["quantity"]
                    price = self._catalog.get(f"{device_name}.{nature_name}.energy_accorded")["price"]
                    money += energy*price

            return money

        for device_name in self._catalog.get("dictionaries")['devices'].keys():
            if self._catalog.get("dictionaries")['devices'][device_name].subclass == subclass:
                self._devices_list[device_name] = [nature.name for nature in self._catalog.get("dictionaries")['devices'][device_name].natures]  # get all the names

        if not self._global:
            self.add(f"simulation_time", graph_status="X")
            self.add(f"physical_time", graph_status=None)

        self.add(f"{subclass}.energy", get_quantity, graph_status="Y")
        self.add(f"{subclass}.money", get_money, graph_status="Y2")


