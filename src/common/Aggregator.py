# This class represents "energy aggregators", i.e a group of devices of the same energy
# we consider that there is a notion of spatial proximity between devices of the same aggregator
# As an example, it can represent a house with a solar panel, the electrical grid of a neighbourhood or a district heating network
from math import inf
from src.tools.GlobalWorld import get_world
default_capacity = {"buying": inf, "selling": inf}


class Aggregator:

    def __init__(self, name, nature, strategy, agent, superior=None, contract=None, efficiency=1, capacity=default_capacity, forecaster=None):
        self._name = name  # the name written in the catalog
        self._nature = nature  # the nature of energy of the aggregator

        self._agent = agent

        self._strategy = strategy  # the strategy, i.e the strategy applied by this aggregator

        self.superior = superior  # the other aggregator this one is obeying to
        # it can be None

        if forecaster:  # if a forecaster is chosen
            self.forecaster = forecaster  # the forecast data
        else:  # a dummy forecaster is created, returning nothing
            # todo: faire un truc propre ?
            class dummy_forecaster():
                def get_predicitions(self):
                    return {"demand": {"value": 0, "uncertainty": 1}, "production": {"value": 0, "uncertainty": 1}}

        self._devices = list()  # a list of the devices managed by the aggregator
        self._subaggregators = list()  # a list of the aggregators managed by the aggregator

        self.quantities = dict()  # a dictionary containing, for each device and each subaggregator, the quantity asked, the price billed, the quantity delivered and the price it cost it

        world = get_world()  # get automatically the world defined for this case
        self._catalog = world.catalog  # the catalog in which some data are stored

        # Creation of specific entries in the catalog
        self._catalog.add(f"{self.name}.energy_bought", {"inside": 0, "outside": 0})  # accounts for the energy bought by the aggregator during the round
        self._catalog.add(f"{self.name}.energy_sold", {"inside": 0, "outside": 0})  # accounts for the energy sold by the aggregator during the round

        self._catalog.add(f"{self.name}.money_spent", {"inside": 0, "outside": 0})  # accounts for the money spent by the aggregator to buy energy during the round
        self._catalog.add(f"{self.name}.money_earned", {"inside": 0, "outside": 0})  # accounts for the money earned by the aggregator by selling energy during the round

        self._catalog.add(f"{self.name}.energy_erased", {"production": 0, "consumption": 0})  # accounts for the money earned by the aggregator by selling energy during the round

        # decision-making values
        self._catalog.add(f"{self.name}.minimum_energy_consumption")
        self._catalog.add(f"{self.name}.maximum_energy_consumption")
        self._catalog.add(f"{self.name}.minimum_energy_production")
        self._catalog.add(f"{self.name}.maximum_energy_production")
        self._catalog.add(f"{self.name}.energy_stored")
        self._catalog.add(f"{self.name}.energy_storable")

        if self.superior:
            self._catalog.add(f"{self.name}.{self.superior.nature.name}.energy_wanted", [])  # couples price/quantities sent by the aggregator to its superior
            self._catalog.add(f"{self.name}.{self.superior.nature.name}.energy_accorded", [])  # couple price/quantities accorded by the aggregator superior
            # the nature of the energy wanted and accorded is that of the superior

        # characteristics of the exchange potential between this aggregator and its superior
        self.efficiency = efficiency
        self.capacity = capacity
        self._contract = contract

        world.register_aggregator(self)  # register the aggregator into world dedicated dictionary

        if nature.name not in self.agent.natures:  # complete the list of natures of the agent
            self.agent._contracts[nature] = None

        try:  # creates an entry for effort in agent if there is not
            self._catalog.add(f"{self.agent.name}.{nature.name}.effort", {"current_round_effort": 0, "cumulated_effort": 0})  # effort accounts for the energy not delivered accordingly to the needs expressed by the agent
        except:
            pass

        try:  # creates an entry for energy erased in agent if there is not
            self._catalog.add(f"{self.agent.name}.{nature.name}.energy_erased", 0)
        except:
            pass

        try:  # creates an entry for energy erased in agent if there is not
            self._catalog.add(f"{self.agent.name}.{nature.name}.energy_bought", 0)
        except:
            pass

        try:  # creates an entry for energy erased in agent if there is not
            self._catalog.add(f"{self.agent.name}.{nature.name}.energy_sold", 0)
        except:
            pass

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

        # decision-making values
        self._catalog.set(f"{self.name}.minimum_energy_consumption", 0)
        self._catalog.set(f"{self.name}.maximum_energy_consumption", 0)
        self._catalog.set(f"{self.name}.minimum_energy_production", 0)
        self._catalog.set(f"{self.name}.maximum_energy_production", 0)
        self._catalog.set(f"{self.name}.energy_stored", 0)
        self._catalog.set(f"{self.name}.energy_storable", 0)

    def ask(self):  # aggregators make local balances and then publish their needs (both in demand and in offer)
        for managed_aggregator in self.subaggregators:  # recursive function to reach all aggregators
            managed_aggregator.ask()

        quantities_and_prices = self._strategy.bottom_up_phase(self)  # makes the balance between local producers and consumers and determines couples price/quantities regarding tariffs and penalties under it

        if quantities_and_prices and self._contract:
            quantities_and_prices = [self._contract.contract_modification(element, self.name) for element in quantities_and_prices]
            self._catalog.set(f"{self.name}.{self.superior.nature.name}.energy_wanted", quantities_and_prices)  # publish its needs
            # the nature of the energy wanted is that of the superior

    def distribute(self):  # aggregators distribute the energy they exchanged with outside
        self._strategy.top_down_phase(self)  # distribute the energy acquired from or sold to the exterior

        for managed_aggregator in self.subaggregators:  # recursive function to reach all aggregators
            managed_aggregator.distribute()

    def check(self):
        self._strategy.check(self)  # distribute the energy acquired from or sold to the exterior

        for managed_aggregator in self.subaggregators:  # recursive function to reach all aggregators
            managed_aggregator.check()

    def make_balances(self):
        for managed_aggregator in self.subaggregators:  # recursive function to reach all aggregators
            managed_aggregator.make_balances()

        # updating balances at the agent level
        energy_sold = sum(self._catalog.get(f"{self.name}.energy_sold").values())
        energy_bought = sum(self._catalog.get(f"{self.name}.energy_bought").values())
        energy_sold_agent = self._catalog.get(f"{self.agent.name}.{self.nature.name}.energy_sold")
        energy_bought_agent = self._catalog.get(f"{self.agent.name}.{self.nature.name}.energy_bought")
        self._catalog.set(f"{self.agent.name}.{self.nature.name}.energy_sold", energy_sold_agent + energy_sold)  # report the energy sold by the aggregator
        self._catalog.set(f"{self.agent.name}.{self.nature.name}.energy_bought", energy_bought_agent + energy_bought)  # report the energy bought by the aggregator

        money_spent = sum(self._catalog.get(f"{self.name}.money_spent").values())
        money_earned = sum(self._catalog.get(f"{self.name}.money_earned").values())
        money_spent_agent = self._catalog.get(f"{self.agent.name}.money_spent")
        money_earned_agent = self._catalog.get(f"{self.agent.name}.money_earned")
        self._catalog.set(f"{self.agent.name}.money_spent", money_spent_agent + money_spent)  # money spent by the aggregator to buy energy during the round
        self._catalog.set(f"{self.agent.name}.money_earned", money_earned_agent + money_earned)  # money earned by the aggregator by selling energy during the round

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    def add_device(self, device_name):  # add the given device_name to the list of devices managed by the aggregator
        self._devices.append(device_name)

    def add_subaggregator(self, subaggregator_name):  # add the given subaggregator_name to the list of subaggregators managed by the aggregator
        self._subaggregators.append(subaggregator_name)

    @property
    def nature(self):  # shortcut for read-only
        return self._nature

    @property
    def name(self):  # shortcut for read-only
        return self._name

    @property
    def strategy(self):  # shortcut for read-only
        return self._strategy

    @property
    def contract(self):  # shortcut for read-only
        return self._contract

    @property
    def agent(self):  # shortcut for read-only
        return self._agent

    @property
    def devices(self):  # shortcut for read-only
        return self._devices

    @property
    def subaggregators(self):  # shortcut for read-only
        return self._subaggregators


