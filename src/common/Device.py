# Root class for all devices constituting a case
# Native packages
from datetime import datetime
from json import load
from math import ceil
# Local packages
from src.tools.Utilities import middle_separation, into_list
from src.tools.GlobalWorld import get_world


class Device:

    def __init__(self, name, contracts, agent, aggregators, filename, profiles, parameters=None):
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

        self._messages = {"bottom-up": {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None},
                         "top-down": {"quantity": 0, "price": 0}}
        self._additional_elements = {}  # additional elements are elements added by users in the message

        aggregators = into_list(aggregators)  # make it iterable
        for aggregator in aggregators:
            if aggregator.nature in self.natures:
                raise DeviceException(f"a aggregator has already been defined for nature {aggregator.nature}")
            else:
                self._natures[aggregator.nature] = {"aggregator": None, "contract": None}
                self._natures[aggregator.nature]["aggregator"] = aggregator

        contracts = into_list(contracts)  # make it iterable
        for contract in contracts:
            if self.natures[contract.nature]["contract"]:
                raise DeviceException(f"a contract has already been defined for nature {contract.nature}")
            else:
                try:  # "try" allows to test if self._natures[nature of the contract] was created in the aggregator definition step
                    self._natures[contract.nature]["contract"] = contract  # add the contract
                    contract.initialization(self.name)
                except:
                    raise DeviceException(f"an aggregator is missing for nature {contract.nature}")

        self._agent = agent  # the agent represents the owner of the device

        # parameters is an optional dictionary which stores additional information needed by user-defined classes
        # putting these information there allow them to be saved/loaded via world method
        if parameters:
            self._parameters = parameters
        else:  # if there are no parameters
            self._parameters = {}  # they are put in an empty dictionary

        world = get_world()  # get automatically the world defined for this case
        self._catalog = world.catalog  # linking the catalog to the device

        world.register_device(self)  # register this device into world dedicated dictionary

        for nature in self.natures:
            if nature not in self.agent.natures:  # complete the list of natures of the agent
                self.agent._contracts[nature] = None

            # messages exchanged
            self._catalog.add(f"{self.name}.{nature.name}.energy_wanted", self._messages["bottom-up"])  # the energy asked or proposed by the device and the price associated
            self._catalog.add(f"{self.name}.{nature.name}.energy_accorded", self._messages["top-down"])  # the energy delivered or accepted by the strategy

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

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def complete_message(self, additional_elements):
        self._additional_elements = additional_elements
        for message in self._messages:
            old_message = self._messages[message]
            self._messages[message] = {**old_message, **additional_elements}

    # ##########################################################################################
    # Consumption reading

    def _read_data_profiles(self, profiles):
        pass

    def _read_consumer_data(self, user_profile):

        # parsing the data
        file = open(self._filename, "r")
        data = load(file)

        # getting the user profile
        try:
            user_data = data["user_profile"][user_profile]
        except:
            raise DeviceException(f"{user_profile} does not belong to the list of predefined user profiles for the class {type(self).__name__}: {data['user_profile'].keys()}")

        return user_data

    def _read_technical_data(self, technical_profile):

        # parsing the data
        file = open(self._filename, "r")
        data = load(file)

        # getting the technical profile
        try:
            technical_data = data["technical_data"][technical_profile]
        except:
            raise DeviceException(f"{technical_profile} does not belong to the list of predefined device profiles for the class {type(self).__name__}: {data['device_consumption'].keys()}")

        file.close()

        return technical_data

    def _data_user_creation(self, data_user):  # modification to enable the device to have a period starting a saturday at 0:00 AM

        # creation of the consumption data
        time_step = self._catalog.get("time_step")
        self._period = max(int(data_user["period"] // time_step), 1)  # the number of rounds corresponding to a period
        # the period MUST be a multiple of the time step

        if type(data_user["offset"]) is float or type(data_user["offset"]) is int:
            self._offset = data_user["offset"]  # the delay between the beginning of the period and the beginning of the year
        elif data_user["offset"] == "Week":  # if the usage takes place the WE, the offset is set at saturday at 0:00 AM
            year = self._catalog.get("physical_time").year  # the year at the beginning of the simulation
            weekday = datetime(year=year, month=1, day=1).weekday()  # the day corresponding to the first day of the year: 0 for Monday, 1 for Tuesday, etc
            offset = weekday  # delay in days between monday and the day

            # without the max(), for a sunday, offset would have been -1, which cause trouble if the period is superior to 1 week
            offset *= 24  # delay in hours between saturday and the day

            self._offset = offset

        time_step = self._catalog.get("time_step")
        year = self._catalog.get("physical_time").year  # the year at the beginning of the simulation
        beginning = self._catalog.get("physical_time") - datetime(year=year, month=1, day=1)  # number of hours elapsed since the beginning of the year
        beginning = beginning.total_seconds() / 3600  # hours -> seconds
        beginning = (beginning - self._offset) / time_step % self._period
        self._moment = ceil(beginning)  # the position in the period where the device starts

        return beginning

    def _unused_nature_removal(self):  # removal of unused natures in the self._natures i.e natures with no profiles
        nature_to_remove = []  # buffer (as it is not possible to remove keys in a dictionary being read)

        for nature in self._natures:
            if nature.name not in self._technical_profile.keys():
                nature_to_remove.append(nature)

        for nature in nature_to_remove:
            self._natures[nature]["aggregator"].devices.remove(self.name)
            self._natures.pop(nature)
            self._catalog.remove(f"{self.name}.{nature.name}.energy_accorded")
            self._catalog.remove(f"{self.name}.{nature.name}.energy_wanted")

    def _randomize_addition(self, value, variation):  # function randomizing by addition, especially used for start time
        variation = self._catalog.get("gaussian")(0, variation)
        value = into_list(value)
        for element in value:
            element += variation % self._period

    def _randomize_multiplication_list(self, value, variation):  # function randomizing by multiplication
        variation = self._catalog.get("gaussian")(1, variation)  # modification of the duration
        variation = max(0, variation)  # to avoid negative durations
        value = into_list(value)  # to avoid to create another function
        for element in value:  # modification of the basic user_profile according to the results of random generation
            element *= variation

    def _randomize_multiplication_dict(self, value, variation):  # function randomizing by multiplication
        variation = self._catalog.get("gaussian")(1, variation)  # modification of the duration
        variation = max(0, variation)  # to avoid negative durations
        value = into_list(value)  # to avoid to create another function
        for element in value:  # modification of the basic user_profile according to the results of random generation
            value[element] *= variation

    def _randomize_multiplication(self, value, variation):  # function randomizing by multiplication
        variation = self._catalog.get("gaussian")(1, variation)  # modification of the duration
        variation = max(0, variation)  # to avoid negative durations
        value *= variation

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def reinitialize(self):  # reinitialization of the balances
        messages = {"bottom-up": {element: self._messages["bottom-up"][element] for element in self._messages["bottom-up"]},
                    "top-down": {element: self._messages["top-down"][element] for element in self._messages["top-down"]}}

        for nature in self.natures:
            # message exchanged
            self._catalog.set(f"{self.name}.{nature.name}.energy_accorded", messages["top-down"])
            self._catalog.set(f"{self.name}.{nature.name}.energy_wanted", messages["bottom-up"])

            # results
            self._catalog.set(f"{self.name}.{nature.name}.energy_erased", 0)
            self._catalog.set(f"{self.name}.{nature.name}.energy_bought", 0)
            self._catalog.set(f"{self.name}.{nature.name}.energy_sold", 0)
            self._catalog.set(f"{self.name}.{nature.name}.money_earned", 0)
            self._catalog.set(f"{self.name}.{nature.name}.money_spent", 0)

    def update(self):  # method updating needs of the devices before the supervision
        pass

    def second_update(self):  # a method used to harmonize aggregator's decisions concerning multi-energy devices
        pass

    def publish_wanted_energy(self, energy_wanted):  # apply the contract to the energy wanted and then publish it in the catalog
        for nature in self.natures:  # publication of the consumption in the catalog
            energy_wanted[nature.name] = self.natures[nature]["contract"].contract_modification(energy_wanted[nature.name], self.name)  # the contract may modify the offer
            self._catalog.set(f"{self.name}.{nature.name}.energy_wanted", energy_wanted[nature.name])  # publication of the message

    def react(self):  # method updating the device according to the decisions taken by the strategy
        for nature in self.natures:
            energy_wanted = self.get_energy_wanted(nature)
            energy_accorded = self.get_energy_accorded(nature)
            [energy_accorded, energy_erased, energy_bought, energy_sold, money_earned, money_spent] = self.natures[nature]["contract"].billing(energy_wanted, energy_accorded, self.name)  # the contract may adjust things
            self.set_energy_accorded(nature, energy_accorded)

            # update of the data at the level of the device
            self._catalog.set(f"{self.name}.{nature.name}.energy_erased", energy_erased)
            self._catalog.set(f"{self.name}.{nature.name}.energy_bought", energy_bought)
            self._catalog.set(f"{self.name}.{nature.name}.energy_sold", energy_sold)
            self._catalog.set(f"{self.name}.{nature.name}.money_earned", money_earned)
            self._catalog.set(f"{self.name}.{nature.name}.money_spent", money_spent)

        if self._moment is not None:
            self._moment = (self._moment + 1) % self._period  # incrementing the hour in the period

    def make_balances(self):  # devices compute the balances for the other objects: contracts, aggregator, agent and nature
        energy_sold = dict()
        energy_bought = dict()
        energy_erased = dict()
        money_spent = dict()
        money_earned = dict()

        additional_elements_value = {element: {} for element in self._additional_elements}  # a summary of all values linked to additionnal elements

        for nature in self.natures:
            energy_erased[nature.name] = self._catalog.get(f"{self.name}.{nature.name}.energy_erased")
            energy_bought[nature.name] = self._catalog.get(f"{self.name}.{nature.name}.energy_bought")
            energy_sold[nature.name] = self._catalog.get(f"{self.name}.{nature.name}.energy_sold")
            money_earned[nature.name] = self._catalog.get(f"{self.name}.{nature.name}.money_earned")
            money_spent[nature.name] = self._catalog.get(f"{self.name}.{nature.name}.money_spent")

            for element in self._additional_elements:
                additional_elements_value[element][nature.name] = self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")[element]

            # balance for different natures
            energy_sold_nature = self._catalog.get(f"{nature.name}.energy_produced")
            energy_bought_nature = self._catalog.get(f"{nature.name}.energy_consumed")
            energy_erased_nature = self._catalog.get(f"{nature.name}.energy_erased")
            money_spent_nature = self._catalog.get(f"{nature.name}.money_spent")
            money_earned_nature = self._catalog.get(f"{nature.name}.money_earned")

            self._catalog.set(f"{nature.name}.energy_produced", energy_sold_nature + energy_sold[nature.name])  # report the energy delivered by the device
            self._catalog.set(f"{nature.name}.energy_consumed", energy_bought_nature + energy_bought[nature.name])  # report the energy consumed by the device
            self._catalog.set(f"{nature.name}.energy_erased", energy_erased_nature + energy_erased[nature.name])  # report the energy consumed by the device
            self._catalog.set(f"{nature.name}.money_spent", money_spent_nature + money_spent[nature.name])  # money spent by the aggregator to buy energy during the round
            self._catalog.set(f"{nature.name}.money_earned", money_earned_nature + money_earned[nature.name])  # money earned by the aggregator by selling energy during the round

            for element in self._additional_elements:
                old_value = self._catalog.get(f"{nature.name}.{element}")
                self._catalog.set(f"{nature.name}.{element}", old_value + additional_elements_value[element][nature.name])

            # balance at the aggregator level
            aggregator = self._natures[nature]["aggregator"]

            energy_bought_inside = self._catalog.get(f"{aggregator.name}.energy_bought")["inside"]  # the device updates the values regarding the inside situation
            energy_bought_outside = self._catalog.get(f"{aggregator.name}.energy_bought")["outside"]  # outside values are left unchanged

            energy_sold_inside = self._catalog.get(f"{aggregator.name}.energy_sold")["inside"]  # the device updates the values regarding the inside situation
            energy_sold_outside = self._catalog.get(f"{aggregator.name}.energy_sold")["outside"]  # outside values are left unchanged

            money_spent_inside = self._catalog.get(f"{aggregator.name}.money_spent")["inside"]  # the device updates the values regarding the inside situation
            money_spent_outside = self._catalog.get(f"{aggregator.name}.money_spent")["outside"]  # outside values are left unchanged

            money_earned_inside = self._catalog.get(f"{aggregator.name}.money_earned")["inside"]  # the device updates the values regarding the inside situation
            money_earned_outside = self._catalog.get(f"{aggregator.name}.money_earned")["outside"]  # outside values are left unchanged

            self._catalog.set(f"{aggregator.name}.energy_bought", {"inside": energy_bought_inside + energy_bought[nature.name], "outside": energy_bought_outside})
            self._catalog.set(f"{aggregator.name}.energy_sold", {"inside": energy_sold_inside + energy_sold[nature.name], "outside": energy_sold_outside})

            self._catalog.set(f"{aggregator.name}.money_spent", {"inside": money_spent_inside + money_spent[nature.name], "outside": money_spent_outside})
            self._catalog.set(f"{aggregator.name}.money_earned", {"inside": money_earned_inside + money_earned[nature.name], "outside": money_earned_outside})

            # balance at the contract level
            energy_sold_contract = self._catalog.get(f"{self.natures[nature]['contract'].name}.energy_sold")
            energy_bought_contract = self._catalog.get(f"{self.natures[nature]['contract'].name}.energy_bought")
            energy_erased_contract = self._catalog.get(f"{self.natures[nature]['contract'].name}.energy_erased")
            money_spent_contract = self._catalog.get(f"{self.natures[nature]['contract'].name}.money_spent")
            money_earned_contract = self._catalog.get(f"{self.natures[nature]['contract'].name}.money_earned")

            self._catalog.set(f"{self.natures[nature]['contract'].name}.energy_sold", energy_sold_contract + energy_sold[nature.name])  # report the energy delivered by the device
            self._catalog.set(f"{self.natures[nature]['contract'].name}.energy_bought", energy_bought_contract + energy_bought[nature.name])  # report the energy consumed by the device
            self._catalog.set(f"{self.natures[nature]['contract'].name}.energy_erased", energy_erased_contract + energy_erased[nature.name])  # report the energy consumed by the device
            self._catalog.set(f"{self.natures[nature]['contract'].name}.money_spent", money_spent_contract + money_spent[nature.name])  # money spent by the contract to buy energy during the round
            self._catalog.set(f"{self.natures[nature]['contract'].name}.money_earned", money_earned_contract + money_earned[nature.name])  # money earned by the contract by selling energy during the round

            for element in self._additional_elements:
                old_value = self._catalog.get(f"{self.natures[nature]['contract'].name}.{element}")
                self._catalog.set(f"{self.natures[nature]['contract'].name}.{element}", old_value + additional_elements_value[element][nature.name])

            # balance at the agent level
            energy_erased_agent = self._catalog.get(f"{self.agent.name}.{nature.name}.energy_erased")
            self._catalog.set(f"{self.agent.name}.{nature.name}.energy_erased", energy_erased_agent + energy_erased[nature.name])  # report the energy consumed by the device

            energy_sold_agent = self._catalog.get(f"{self.agent.name}.{nature.name}.energy_sold")
            energy_bought_agent = self._catalog.get(f"{self.agent.name}.{nature.name}.energy_bought")
            self._catalog.set(f"{self.agent.name}.{nature.name}.energy_sold", energy_sold_agent + energy_sold[nature.name])  # report the energy delivered by the device
            self._catalog.set(f"{self.agent.name}.{nature.name}.energy_bought", energy_bought_agent + energy_bought[nature.name])  # report the energy consumed by the device

            money_spent_agent = self._catalog.get(f"{self.agent.name}.money_spent")
            money_earned_agent = self._catalog.get(f"{self.agent.name}.money_earned")
            self._catalog.set(f"{self.agent.name}.money_spent", money_spent_agent + sum(money_spent.values()))  # money spent by the aggregator to buy energy during the round
            self._catalog.set(f"{self.agent.name}.money_earned", money_earned_agent + sum(money_earned.values()))  # money earned by the aggregator by selling energy during the round

            for element in self._additional_elements:
                old_value = self._catalog.get(f"{self.agent.name}.{element}")
                self._catalog.set(f"{self.agent.name}.{element}", old_value + sum(additional_elements_value[element].values()))

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    # getter/setter for the accorded energy
    def get_energy_accorded(self, nature):  # return the full message of energy accorded by the device during the round
        return self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")

    def set_energy_accorded(self, nature, value):  # set the quantity of energy accorded to the device during the round
        energy_accorded = value
        self._catalog.set(f"{self.name}.{nature.name}.energy_accorded", energy_accorded)

    def get_energy_accorded_quantity(self, nature):  # return the quantity of energy accorded to the device during the round
        return self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")["quantity"]

    def set_energy_accorded_quantity(self, nature, value):  # set the quantity of energy accorded to the device during the round
        energy_accorded = self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")
        energy_accorded["quantity"] = value
        self._catalog.set(f"{self.name}.{nature.name}.energy_accorded", energy_accorded)

    def get_energy_accorded_price(self, nature):  # return the price of the energy accorded to the device during the round
        return self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")["price"]

    def set_energy_accorded_price(self, nature, value):  # set the price of the energy accorded to the device during the round
        energy_accorded = self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")
        energy_accorded["price"] = value
        self._catalog.set(f"{self.name}.{nature.name}.energy_accorded", energy_accorded)

    # getter/setter for the wanted energy
    def get_energy_wanted(self, nature):  # return the full message of energy wanted by the device during the round
        return self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")

    def get_energy_wanted_min(self, nature):  # return the minimum quantity of energy wanted by the device during the round
        return self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")["energy_minimum"]

    def get_energy_wanted_nom(self, nature):  # return the nominal quantity of energy wanted by the device during the round
        return self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")["energy_nominal"]

    def get_energy_wanted_max(self, nature):  # return the maximum quantity of energy wanted by the device during the round
        return self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")["energy_maximum"]

    def get_energy_wanted_price(self, nature):  # return the price for the quantity of energy wanted by the device during the round
        return self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")["price"]

    def set_energy_wanted_quantity(self, nature, Emin, Enom, Emax):  # set the quantity of energy wanted by the device during the round
        energy_wanted = self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")
        energy_wanted["energy_minimum"] = Emin
        energy_wanted["energy_nominal"] = Enom
        energy_wanted["energy_maximum"] = Emax
        self._catalog.set(f"{self.name}.{nature.name}.energy_wanted", energy_wanted)

    def set_energy_wanted_price(self, nature, value):  # set the price for the quantity of energy wanted by the device during the round
        energy_wanted = self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")
        energy_wanted["price"] = value
        self._catalog.set(f"{self.name}.{nature.name}.energy_wanted", energy_wanted)

    @property
    def name(self):  # shortcut for read-only
        return self._name

    @property
    def natures(self):  # shortcut for read-only
        return self._natures

    @property
    def agent(self):  # shortcut for read-only
        return self._agent

    @property
    def subclass(self):
        return self.__class__.__name__

    def __str__(self):
        return middle_separation + f"\nDevice {self.name} of type {self.__class__.__name__}"


# Exception
class DeviceException(Exception):
    def __init__(self, message):
        super().__init__(message)


