# This object represents the conversion points between 2 clusters.
# For the downstream cluster, it looks like a conversion point, but, for the upstream cluster, it looks like a device
# The main difference between a conversion point and a device is the following: when the device is a "customer" for the aggregator, it is the aggregator who is the customer of the conversion point.
from src.tools.Utilities import into_list


class Converter:

    def __init__(self, name, contract, agent, filename, upstream_cluster, downstream_cluster, usage_profile_name, parameters=None):
        self._name = name  # the name which serve as root in the catalog entries

        self._filename = filename  # the name of the data file

        self._moment = None  # the current moment in the period
        self._period = None  # the duration of a classic cycle of use for the user of the device
        self._offset = None  # the delay between the beginning of the period and the beginning of the year

        self._usage_profile_name = usage_profile_name
        self._usage_profile = []  # energy profile for one usage of the device
        # the content differs depending on the kind of device

        self._agent = agent  # the agent represents the owner of the converter

        self._upstream_cluster = upstream_cluster  # the cluster where the energy come from
        self._downstream_cluster = downstream_cluster  # the cluster where the energy goes to

        self._natures = {"upstream": upstream_cluster.nature,
                         "downstream": downstream_cluster.nature}

        if self.natures[contract.nature] != downstream_cluster.nature:
            raise ConverterException(f"a contract has already been defined for nature {contract.nature}")

        self._catalog = None  # added later

        # parameters is an optional dictionary which stores additional information needed by user-defined classes
        # putting these information there allow them to be saved/loaded via world method
        if parameters:
            self._parameters = parameters
        else:  # if there are no parameters
            self._parameters = {}  # they are put in an empty dictionary

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register(self, catalog):  # make the initialization operations undoable without a catalog
        self._catalog = catalog  # linking the catalog to the device

        # regarding the upstream aggregator
        # it looks like a device
        self._catalog.add(f"{self.name}.{self.natures['upstream'].name}.energy_wanted", {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None})  # the energy asked or proposed by the converter and the price associated
        self._catalog.add(f"{self.name}.{self.natures['upstream'].name}.energy_accorded", {"quantity": 0, "price": 0})  # the energy delivered or accepted by the supervisor

        # regarding the downstream aggregator
        # it looks like a converter
        self._catalog.add(f"{self.name}.{self.natures['upstream'].name}.energy_wanted", {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None})  # the energy asked or proposed by the device ant the price associated
        self._catalog.add(f"{self.name}.{self.natures['upstream'].name}.energy_accorded", {"quantity": 0, "price": 0})  # the energy delivered or accepted by the supervisor

        # regarding the agent
        for nature in self._natures.values():
            if nature not in self.agent.natures:  # complete the list of natures of the agent
                self.agent._contracts[nature] = None

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

        self._user_register()  # here the possibility is let to the user to modify things according to his needs

    def _user_register(self):  # where users put device-specific behaviors
        pass

    def _get_consumption(self):
        pass

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def reinitialize(self):  # reinitialization of the balances
        self._catalog.set(f"{self.name}.{self.natures['upstream'].name}.energy_accorded", {"quantity": 0, "price": 0})
        self._catalog.set(f"{self.name}.{self.natures['upstream'].name}.energy_wanted", {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None})

    def update(self):  # method updating needs of the devices before the supervision
        pass

    def toto(self):  # this method updates the quantities asked to the upstream cluster according to the ones asked by the downstream cluster
        pass

    def react(self):  # method updating the device according to the decisions taken by the supervisor
        self._user_react()

        energy_sold = dict()
        energy_bought = dict()
        energy_erased = dict()
        money_spent = dict()
        money_earned = dict()

        for nature in self._natures:
            energy_amount = self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")["quantity"]
            energy_wanted = self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")["energy_maximum"]
            price = self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")["price"]

            if energy_amount < 0:  # if the device consumes energy
                energy_sold[nature.name] = energy_amount
                energy_bought[nature.name] = 0
                money_earned[nature.name] = price * energy_amount
                money_spent[nature.name] = 0

            else:  # if the device delivers energy
                energy_bought[nature.name] = energy_amount
                energy_sold[nature.name] = 0
                money_earned[nature.name] = 0
                money_spent[nature.name] = price * energy_amount

            energy_erased[nature.name] = abs(energy_amount - energy_wanted)  # energy refused to the device by the supervisor

            # balance for different natures
            energy_sold_nature = - self._catalog.get(f"{nature.name}.energy_produced")
            energy_bought_nature = self._catalog.get(f"{nature.name}.energy_consumed")
            money_spent_nature = self._catalog.get(f"{nature.name}.money_spent")
            money_earned_nature = self._catalog.get(f"{nature.name}.money_earned")

            self._catalog.set(f"{nature.name}.energy_produced", energy_sold_nature + energy_sold[nature.name])  # report the energy delivered by the device
            self._catalog.set(f"{nature.name}.energy_consumed", energy_bought_nature + energy_bought[nature.name])  # report the energy consumed by the device
            self._catalog.set(f"{nature.name}.money_spent", money_spent_nature + money_spent[nature.name])  # money spent by the cluster to buy energy during the round
            self._catalog.set(f"{nature.name}.money_earned", money_earned_nature - money_earned[nature.name])  # money earned by the cluster by selling energy during the round

            # balance at the contract level
            energy_sold_contract = self._catalog.get(f"{self.natures[nature]['contract'].name}.energy_sold")
            energy_bought_contract = self._catalog.get(f"{self.natures[nature]['contract'].name}.energy_bought")
            money_spent_contract = self._catalog.get(f"{self.natures[nature]['contract'].name}.money_spent")
            money_earned_contract = self._catalog.get(f"{self.natures[nature]['contract'].name}.money_earned")

            self._catalog.set(f"{self.natures[nature]['contract'].name}.energy_sold", energy_sold_contract + energy_sold[nature.name])  # report the energy delivered by the device
            self._catalog.set(f"{self.natures[nature]['contract'].name}.energy_bought", energy_bought_contract + energy_bought[nature.name])  # report the energy consumed by the device
            self._catalog.set(f"{self.natures[nature]['contract'].name}.money_spent", money_spent_contract + money_spent[nature.name])  # money spent by the contract to buy energy during the round
            self._catalog.set(f"{self.natures[nature]['contract'].name}.money_earned", money_earned_contract - money_earned[nature.name])  # money earned by the contract by selling energy during the round

        # balance at the agent level
        for nature in self.natures:
            energy_erased_agent = self._catalog.get(f"{self.agent.name}.{nature.name}.energy_erased")
            self._catalog.set(f"{self.agent.name}.{nature.name}.energy_erased", energy_erased_agent + energy_erased[nature.name])  # report the energy consumed by the device

            energy_sold_agent = self._catalog.get(f"{self.agent.name}.{nature.name}.energy_sold")
            energy_bought_agent = self._catalog.get(f"{self.agent.name}.{nature.name}.energy_bought")
            self._catalog.set(f"{self.agent.name}.{nature.name}.energy_sold", energy_sold_agent + energy_sold[nature.name])  # report the energy delivered by the device
            self._catalog.set(f"{self.agent.name}.{nature.name}.energy_bought", energy_bought_agent + energy_bought[nature.name])  # report the energy consumed by the device

        money_spent_agent = self._catalog.get(f"{self.agent.name}.money_spent")
        money_earned_agent = self._catalog.get(f"{self.agent.name}.money_earned")

        self._catalog.set(f"{self.agent.name}.money_spent", money_spent_agent + sum(money_spent.values()))  # money spent by the cluster to buy energy during the round
        self._catalog.set(f"{self.agent.name}.money_earned", money_earned_agent - sum(money_earned.values()))  # money earned by the cluster by selling energy during the round

    def _user_react(self):  # where users put device-specific behaviors
            pass

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def name(self):  # shortcut for read-only
        return self._name

    @property
    def natures(self):  # shortcut for read-only
        return self._natures

    @property
    def usage_profile(self):  # shortcut for read-only
        return self._usage_profile_name

    @property
    def agent(self):  # shortcut for read-only
        return self._agent


# Exception
class ConverterException(Exception):
    def __init__(self, message):
        super().__init__(message)


