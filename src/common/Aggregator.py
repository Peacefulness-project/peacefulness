# This class represents "energy aggregators", i.e a group of devices of the same energy
# we consider that there is a notion of spatial proximity between devices of the same aggregator
# As an example, it can represent a house with a solar panel, the electrical grid of a neighbourhood or a district heating network
from math import inf
from src.tools.GlobalWorld import get_world


class Aggregator:

    def __init__(self, name, nature, strategy, agent, superior=None, contract=None, efficiency=1, capacity=inf):
        self._name = name  # the name written in the catalog
        self._nature = nature  # the nature of energy of the aggregator

        self._agent = agent

        self._strategy = strategy  # the strategy, i.e the strategy applied by this aggregator

        self.superior = superior  # the other aggregator this one is obeying to
        # It can be None

        self._devices = list()  # a list of the devices managed by the aggregator
        self._subaggregators = list()  # a list of the aggregators managed by the aggregator
        self._converters = list()  # a list of the converters available for the aggregator

        self.quantities = dict()  # a dictionary containing, for each device and each subaggregator, the quantity asked, the price billed, the quantity delivered and the price it cost it

        world = get_world()  # get automatically the world defined for this case
        self._catalog = world.catalog  # the catalog in which some data are stored

        # Creation of specific entries in the catalog
        self._catalog.add(f"{self.name}.energy_bought", {"inside": 0, "outside": 0})  # accounts for the energy bought by the aggregator during the round
        self._catalog.add(f"{self.name}.energy_sold", {"inside": 0, "outside": 0})  # accounts for the energy sold by the aggregator during the round

        self._catalog.add(f"{self.name}.money_spent", {"inside": 0, "outside": 0})  # accounts for the money spent by the aggregator to buy energy during the round
        self._catalog.add(f"{self.name}.money_earned", {"inside": 0, "outside": 0})  # accounts for the money earned by the aggregator by selling energy during the round

        if self.superior:
            self._catalog.add(f"{self.name}.{self.superior.nature.name}.energy_wanted", [])  # couples price/quantities sent by the aggregator to its superior
            self._catalog.add(f"{self.name}.{self.superior.nature.name}.energy_accorded", [])  # couple price/quantities accorded by the aggregator superior
            # the nature of the energy wanted and accorded is that of the superior

            # characteristics of the exchange potential between this aggregator and its superior
            self.efficiency = efficiency
            self.capacity = capacity
            self._contract = contract

        world.register_aggregator(self)  # register the aggregator into world dedicated dictionary

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def reinitialize(self):  # reinitialization of the values
        if self.superior:
            self._catalog.set(f"{self.name}.{self.superior.nature.name}.energy_wanted", [])  # couples price/quantities sent by the aggregator to its superior
            self._catalog.set(f"{self.name}.{self.superior.nature.name}.energy_accorded", [])  # couple price/quantities accorded by the aggregator superior
            # the nature of the energy wanted and accorded is that of the superior

        self._catalog.set(f"{self.name}.energy_bought", {"inside": 0, "outside": 0})  # accounts for the energy bought by the aggregator during the round
        self._catalog.set(f"{self.name}.energy_sold", {"inside": 0, "outside": 0})  # accounts for the energy sold by the aggregator during the round

        self._catalog.set(f"{self.name}.money_spent", {"inside": 0, "outside": 0})  # accounts for the money spent by the aggregator to buy energy during the round
        self._catalog.set(f"{self.name}.money_earned", {"inside": 0, "outside": 0})  # accounts for the money earned by the aggregator by selling energy during the round

    def ask(self):  # aggregators make local balances and then publish their needs (both in demand and in offer)
        for managed_aggregator in self.subaggregators:  # recursive function to reach all aggregators
            managed_aggregator.ask()

        quantities_and_prices = self._strategy.ascendant_phase(self)  # makes the balance between local producers and consumers and determines couples price/quantities regarding tariffs and penalties under it

        if quantities_and_prices:
            quantities_and_prices = [self._contract.contract_modification(element) for element in quantities_and_prices]
            self._catalog.set(f"{self.name}.{self.superior.nature.name}.energy_wanted", quantities_and_prices)  # publish its needs
            # the nature of the energy wanted is that of the superior

    def distribute(self):  # aggregators distribute the energy they exchanged with outside
        self._strategy.distribute_remote_energy(self)  # distribute the energy acquired from or sold to the exterior

        for managed_aggregator in self.subaggregators:  # recursive function to reach all aggregators
            managed_aggregator.distribute()

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    def add_device(self, device_name):  # add the given device_name to the list of devices managed by the aggregator
        self._devices.append(device_name)

    def add_subaggregator(self, subaggregator_name):  # add the given subaggregator_name to the list of subaggregators managed by the aggregator
        self._subaggregators.append(subaggregator_name)

    def add_converter(self, converter_name):  # add the given converter_name to the list of converters managed by the aggregator
        self._converters.append(converter_name)

    @property
    def nature(self):  # shortcut for read-only
        return self._nature

    @property
    def name(self):  # shortcut for read-only
        return self._name

    @property
    def devices(self):  # shortcut for read-only
        return self._devices

    @property
    def subaggregators(self):  # shortcut for read-only
        return self._subaggregators

    @property
    def converters(self):  # shortcut for read-only
        return self._converters
