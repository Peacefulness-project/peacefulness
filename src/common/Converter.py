# A converter transfers energy from one aggregator (upstream) of energy A to another aggregator (downstream) of energy B.
# For the downstream aggregator, it looks like a conversion point, but, for the upstream aggregator, it looks like a device.
# The main difference between a conversion point and a device is the following: when the device is a "customer" for the aggregator, it is the aggregator who is the customer of the conversion point.
from json import load
from src.tools.GlobalWorld import get_world


class Converter:

    def __init__(self, name, contract, agent, filename, upstream_aggregator, downstream_aggregator, technical_profile_name, parameters=None):
        self._name = name  # the name which serve as root in the catalog entries

        self._filename = filename  # the name of the data file

        self._technical_profile_name = technical_profile_name
        self._usage_profile = []  # technical characteristics of this converter

        self._agent = agent  # the agent represents the owner of the converter

        self._aggregators = {"upstream_aggregator": upstream_aggregator, "downstream_aggregator": downstream_aggregator}  # the aggregators the converter is linked to

        self._price = 0.05  # todo: virer ce truc et créer contrats ad hoc

        self._natures = {"upstream": upstream_aggregator.nature,
                         "downstream": downstream_aggregator.nature}

        if contract.nature != upstream_aggregator.nature:
            raise ConverterException(f"the contract has to be defined for nature {contract.nature.name}")
        self._contract = contract

        world = get_world()  # get automatically the world defined for this case
        self._catalog = world.catalog  # linking the catalog to the device

        world.register_converter(self)

        # parameters is an optional dictionary which stores additional information needed by user-defined classes
        # putting these information there allow them to be saved/loaded via world method
        if parameters:
            self._parameters = parameters
        else:  # if there are no parameters
            self._parameters = {}  # they are put in an empty dictionary

        # regarding the upstream aggregator
        # it looks like a device
        self._catalog.add(f"{self.name}.{self.natures['upstream'].name}.energy_wanted", {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None})  # the energy asked or proposed by the converter and the price associated
        self._catalog.add(f"{self.name}.{self.natures['upstream'].name}.energy_accorded", {"quantity": 0, "price": 0})  # the energy delivered by the upstream aggregator

        # regarding the downstream aggregator
        # it looks like a converter
        self._catalog.add(f"{self.name}.{self.natures['downstream'].name}.energy_wanted", {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None})  # the energy proposed by the converter and the price associated
        self._catalog.add(f"{self.name}.{self.natures['downstream'].name}.energy_asked", {"quantity": 0, "price": 0})  # the energy wanted by the downstream aggregator
        self._catalog.add(f"{self.name}.{self.natures['downstream'].name}.energy_accorded", {"quantity": 0, "price": 0})  # the quantity of energy really furnished to the downstream aggregator

        # regarding the agent
        for nature in self._natures.values():
            if nature not in self.agent.natures:  # complete the list of natures of the agent
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

        self._get_technical_data()

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _get_technical_data(self):
        pass

    def _read_technical_data(self):

        # parsing the data
        file = open(self._filename, "r")
        data = load(file)

        # getting the usage profile
        try:
            data = data[self._technical_profile_name]
        except:
            raise ConverterException(f"{self._technical_profile_name} does not belong to the list of predefined profiles for the class {type(self).__name__}")

        file.close()

        return data

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def reinitialize(self):  # reinitialization of the balances
        # for the upstream aggregator, the converter is a normal device
        self._catalog.set(f"{self.name}.{self.natures['upstream'].name}.energy_accorded", {"quantity": 0, "price": 0})
        self._catalog.set(f"{self.name}.{self.natures['upstream'].name}.energy_wanted", {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None})

        # for the downstream aggregator, the converter is a converter, i.e a potential source of energy
        self._catalog.set(f"{self.name}.{self.natures['downstream'].name}.energy_wanted", {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None})  # the proposal made to the downstream aggregator
        self._catalog.set(f"{self.name}.{self.natures['downstream'].name}.energy_asked", {"quantity": 0, "price": 0})  # the quantitiy asked by the downstream aggregator
        self._catalog.set(f"{self.name}.{self.natures['downstream'].name}.energy_accorded", {"quantity": 0, "price": 0})  # the quantity furnished by the converter to the downstream aggregator

    def first_update(self):  # this method updates the quantities asked to the upstream aggregator according to the ones asked by the downstream aggregator
        pass

    def second_update(self):  # method updating the converter between the ascendant phase of the downstream aggregator and of the upstream aggregator
        pass

    def first_react(self):  # this method adapts the converter to the decision taken by the upstream aggregator
        pass

    def second_react(self):  # method updating the device according to the decisions taken by the supervisor
        self._user_react()

        energy_sold = dict()
        energy_bought = dict()
        energy_erased = dict()
        money_spent = dict()
        money_earned = dict()

        for nature in self._natures.values():
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
            self._catalog.set(f"{nature.name}.money_spent", money_spent_nature + money_spent[nature.name])  # money spent by the aggregator to buy energy during the round
            self._catalog.set(f"{nature.name}.money_earned", money_earned_nature - money_earned[nature.name])  # money earned by the aggregator by selling energy during the round

            # balance at the contract level
            energy_sold_contract = self._catalog.get(f"{self.contract.name}.energy_sold")
            energy_bought_contract = self._catalog.get(f"{self.contract.name}.energy_bought")
            money_spent_contract = self._catalog.get(f"{self.contract.name}.money_spent")
            money_earned_contract = self._catalog.get(f"{self.contract.name}.money_earned")

            self._catalog.set(f"{self.contract.name}.energy_sold", energy_sold_contract + energy_sold[nature.name])  # report the energy delivered by the device
            self._catalog.set(f"{self.contract.name}.energy_bought", energy_bought_contract + energy_bought[nature.name])  # report the energy consumed by the device
            self._catalog.set(f"{self.contract.name}.money_spent", money_spent_contract + money_spent[nature.name])  # money spent by the contract to buy energy during the round
            self._catalog.set(f"{self.contract.name}.money_earned", money_earned_contract - money_earned[nature.name])  # money earned by the contract by selling energy during the round

        # balance at the agent level
        for nature in self.natures.values():
            energy_erased_agent = self._catalog.get(f"{self.agent.name}.{nature.name}.energy_erased")
            self._catalog.set(f"{self.agent.name}.{nature.name}.energy_erased", energy_erased_agent + energy_erased[nature.name])  # report the energy consumed by the device

            energy_sold_agent = self._catalog.get(f"{self.agent.name}.{nature.name}.energy_sold")
            energy_bought_agent = self._catalog.get(f"{self.agent.name}.{nature.name}.energy_bought")
            self._catalog.set(f"{self.agent.name}.{nature.name}.energy_sold", energy_sold_agent + energy_sold[nature.name])  # report the energy delivered by the device
            self._catalog.set(f"{self.agent.name}.{nature.name}.energy_bought", energy_bought_agent + energy_bought[nature.name])  # report the energy consumed by the device

        money_spent_agent = self._catalog.get(f"{self.agent.name}.money_spent")
        money_earned_agent = self._catalog.get(f"{self.agent.name}.money_earned")

        self._catalog.set(f"{self.agent.name}.money_spent", money_spent_agent + sum(money_spent.values()))  # money spent by the aggregator to buy energy during the round
        self._catalog.set(f"{self.agent.name}.money_earned", money_earned_agent - sum(money_earned.values()))  # money earned by the aggregator by selling energy during the round

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
        return self._technical_profile_name

    @property
    def agent(self):  # shortcut for read-only
        return self._agent

    @property
    def aggregators(self):  # shortcut for read-only
        return self._aggregators

    @property
    def contract(self):  # shortcut for read-only
        return self._contract


# Exception
class ConverterException(Exception):
    def __init__(self, message):
        super().__init__(message)


