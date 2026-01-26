# This subclass of Converter represents "lateral" energy exchanges between aggregators of the same energy carriers.
# Meanwhile, for the moment, it is considered possible to put it on/off instantly.
from src.common.DeviceMainClasses import Converter, into_list
from src.common.World import World

class DummyConverter(Converter):

    def __init__(self, name, contracts, agent, upstream_aggregator, downstream_aggregator, profiles, parameters=None, filename="lib/Subclasses/Device/DummyConverter/DummyConverter.json"):
        upstream_aggregators_list = into_list(upstream_aggregator)
        downstream_aggregators_list = into_list(downstream_aggregator)

        self._name = name  # the name which serve as root in the catalog entries

        self._filename = filename  # the name of the data file

        self._moment = None  # the current moment in the period
        self._period = None  # the duration of a classic cycle of use for the user of the device
        self._offset = None  # the delay between the beginning of the period and the beginning of the year

        self._user_profile = list()  # user profile of utilisation, describing user's priority
        # the content differs depending on the kind of device

        self._technical_profile = list()  # energy profile for one usage of the device
        # the content differs depending on the kind of device

        # here are data dicts dedicated to different levels of energy needed/proposed each turn
        # 1 key <=> 1 energy nature
        self._natures = dict()  # contains, for each energy nature used by the device, the aggregator and the nature associated

        aggregators = into_list(upstream_aggregators_list + downstream_aggregators_list)  # make it iterable
        for aggregator in aggregators:
            if aggregator.nature in self.natures:
                self._natures[aggregator.nature].append({"aggregator": None, "contract": None})
                self._natures[aggregator.nature][-1]["aggregator"] = aggregator
            else:
                self._natures[aggregator.nature] = [{"aggregator": None, "contract": None}]
                self._natures[aggregator.nature][-1]["aggregator"] = aggregator

        contracts = into_list(contracts)  # make it iterable
        for contract in contracts:
            for tup in self._natures[contract.nature]:
                try:  # "try" allows to test if self._natures[nature of the contract] was created in the aggregator definition step
                    tup["contract"] = contract  # add the contract
                    contract.initialization(self.name)
                except:
                    raise Exception(f"an aggregator is missing for nature {contract.nature}")

        self._agent = agent  # the agent represents the owner of the device

        # parameters is an optional dictionary which stores additional information needed by user-defined classes
        # putting these information there allow them to be saved/loaded via world method
        if parameters:
            self._parameters = parameters
        else:  # if there are no parameters
            self._parameters = {}  # they are put in an empty dictionary

        world = World.ref_world  # get automatically the world defined for this case
        self._catalog = world.catalog  # linking the catalog to the device

        world.register_device(self)  # register this device into world dedicated dictionary

        for nature in self.natures:
            if nature not in self.agent.natures:  # complete the list of natures of the agent
                self.agent._contracts[nature] = None

            # messages exchanged
            self._catalog.add(f"{self.name}.{nature.name}.energy_wanted", self.__class__.information_message())  # the energy asked or proposed by the device and the price associated
            self._catalog.add(f"{self.name}.{nature.name}.energy_accorded", self.__class__.decision_message())  # the energy delivered or accepted by the strategy

            # results
            self._catalog.add(f"{self.name}.{nature.name}.energy_erased", 0)
            self._catalog.add(f"{self.name}.{nature.name}.energy_bought", 0)
            self._catalog.add(f"{self.name}.{nature.name}.energy_sold", 0)
            self._catalog.add(f"{self.name}.{nature.name}.money_earned", 0)
            self._catalog.add(f"{self.name}.{nature.name}.money_spent", 0)

            try:  # creates an entry for effort in agent if there is not
                self._catalog.add(f"{self.agent.name}.{nature.name}.effort", {"current_round_effort": 0, "cumulated_effort": 0})  # effort accounts for the energy not delivered accordingly to the needs expressed by the agent
            except:
                pass
            try:  # creates an entry useful for results
                self._catalog.add(f"{self.agent.name}.{nature.name}.energy_erased", 0)
                self._catalog.add(f"{self.agent.name}.{nature.name}.energy_bought", 0)
                self._catalog.add(f"{self.agent.name}.{nature.name}.energy_sold", 0)
            except:
                pass

        if self._filename != "loaded device":  # if a filename has been defined...
            self._read_data_profiles(profiles)  # ... then the file is converted into consumption profiles
            # else, the device has been loaded and does not need a data file

        contracts = {contract.nature.name: contract for contract in contracts}
        self._upstream_aggregators_list = [{"name": aggregator.name, "nature": aggregator.nature.name, "contract": contracts[aggregator.nature.name]} for aggregator in upstream_aggregators_list]  # list of aggregators involved in the production of energy. The order is not important.
        self._downstream_aggregators_list = [{"name": aggregator.name, "nature": aggregator.nature.name, "contract": contracts[aggregator.nature.name]} for aggregator in downstream_aggregators_list]  # list of aggregators involved in the consumption of energy. The order is important: the first aggregator defines the final quantity of energy

        time_step = self._catalog.get("time_step")
        self._energy_physical_limits = {"minimum_energy": 0, "maximum_energy": parameters["max_power"] * time_step}

        for aggregator in self._downstream_aggregators_list:
            nature_name = aggregator["nature"]
            self._catalog.add(f"{self.name}.{nature_name}.efficiency", None)


