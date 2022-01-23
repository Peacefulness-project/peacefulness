    # Contract are objects used to enable/disable certain operations during the supervision
# They also serve to specify the way of billing the agents
from src.tools.GlobalWorld import get_world


class Contract:

    def __init__(self, name, nature, daemon, parameters=None):
        self._name = name
        self._nature = nature

        self.description = ""  # a brief description of the contract

        self._daemon_name = daemon.name

        # parameters is an optional dictionary which stores additional information needed by user-defined classes
        # putting these information there allow them to be saved/loaded via world method
        if parameters:
            self._parameters = parameters
        else:  # if there are no parameters
            self._parameters = {}  # they are put in an empty dictionary

        world = get_world()  # get automatically the world defined for this case
        self._catalog = world.catalog

        # Creation of specific entries
        self._catalog.add(f"{self.name}.money_earned", 0)  # the money earned by all the devices ruled to this contract during this round
        self._catalog.add(f"{self.name}.money_spent", 0)  # the money spent by all the devices ruled by this contract during this round

        self._catalog.add(f"{self.name}.energy_bought", 0)  # the energy bought by all the devices attached to this contract during this round
        self._catalog.add(f"{self.name}.energy_sold", 0)  # the energy sold by all the devices attached to this contract during this round
        self._catalog.add(f"{self.name}.energy_erased", 0)  # the sum of energy erased by all the devices attached to this contract during the round

        world.register_contract(self)  # register this contract into world dedicated dictionary

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def initialization(self, device_name):  # a method allowing the contract to do something when a dice suscribe to it
        pass

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def reinitialize(self):  # reinitialization of the values
        self._catalog.set(f"{self.name}.money_earned", 0)  # the money earned by all the devices ruled to this contract during this round
        self._catalog.set(f"{self.name}.money_spent", 0)  # the money spent by all the devices ruled by this contract during this round

        self._catalog.set(f"{self.name}.energy_bought", 0)  # the energy bought by all the devices attached to this contract during this round
        self._catalog.set(f"{self.name}.energy_sold", 0)  # the energy sold by all the devices attached to this contract during this round
        self._catalog.set(f"{self.name}.energy_erased", 0)  # the sum of energy erased by all the devices attached to this contract during the round

        for element in self._catalog.get("additional_elements"):
            self._catalog.set(f"{self.name}.{element}", self._catalog.get("additional_elements")[element])

    # quantities management
    def contract_modification(self, quantity, name):  # this function adds a price to the information sent by the device and may modfy other things, such as emergency
        pass  # a method to determine the price must be defined in the subclasses

    def billing(self, energy_wanted, energy_accorded, name):  # the action of the distribution phase
        energy_wanted = energy_wanted["energy_maximum"]
        energy_served = energy_accorded["quantity"]
        price = energy_accorded["price"]

        if energy_served < 0:  # if the device delivers energy
            energy_sold = - energy_served
            energy_bought = 0
            money_earned = - price * energy_served
            money_spent = 0

        else:  # if the device consumes energy
            energy_bought = energy_served
            energy_sold = 0
            money_earned = 0
            money_spent = price * energy_served

        energy_erased = abs(energy_served - energy_wanted)  # energy refused to the device by the strategy

        return [energy_accorded, energy_erased, energy_bought, energy_sold, money_earned, money_spent]  # if the function is not modified, it does not change the initial value

    # ##########################################################################################
    # Utilities
    # ##########################################################################################

    @property
    def name(self):  # shortcut for read-only
        return self._name

    @property
    def nature(self):  # shortcut for read-only
        return self._nature

    @property
    def buying_price(self):  # shortcut for read-only
        return self._catalog.get(f"{self._daemon_name}.buying_price")

    @property
    def selling_price(self):  # shortcut for read-only
        return self._catalog.get(f"{self._daemon_name}.selling_price")
