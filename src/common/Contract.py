# Contract are objects used to enable/disable certain operations during the supervision
# They also serve to specify the way of billing the agents


class Contract:

    def __init__(self, world, name, nature, identifier, parameters=None):
        self._name = name
        self._catalog = world.catalog
        self._nature = nature

        self.description = ""  # a brief description of the contract

        self._identifier = identifier

        # parameters is an optional dictionary which stores additional information needed by user-defined classes
        # putting these information there allow them to be saved/loaded via world method
        if parameters:
            self._parameters = parameters
        else:  # if there are no parameters
            self._parameters = {}  # they are put in an empty dictionary

        self._catalog.add(f"{self.name}.buying_price", None)  # the price paid to buy energy of a given nature with this contract
        self._catalog.add(f"{self.name}.selling_price", None)  # the price received by selling energy  of a given nature with this contract

        self._user_register()

        self._define_prices()  # add this contract to a list of contracts of the same identifier
        # it means that prices are set by the same daemon

        # Creation of specific entries
        self._catalog.add(f"{self.name}.money_earned", 0)  # the money earned by all the devices ruled to this contract during this round
        self._catalog.add(f"{self.name}.money_spent"), 0  # the money spent by all the devices ruled by this contract during this round

        self._catalog.add(f"{self.name}.energy_bought", 0)  # the energy bought by all the devices attached to this contract during this round
        self._catalog.add(f"{self.name}.energy_sold", 0)  # the energy sold by all the devices attached to this contract during this round

        world.register_contract(self)  # register this contract into world dedicated dictionary

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _define_prices(self):
        try:  # if it is the first contract of its class and nature, it creates an entry repertoring all contracts of its class and nature in the catalog
            # later, a daemon in charge of setting prices saves the list and removes this entry
            self._catalog.add(f"contracts_{self._identifier}", [])
        except:
            pass

        contract_list = self._catalog.get(f"contracts_{self._identifier}")
        contract_list.append(self.name)
        self._catalog.set(f"contracts_{self._identifier}", contract_list)

    def _user_register(self):
        pass

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def reinitialize(self):  # reinitialization of the values
        self._catalog.set(f"{self.name}.money_earned", 0)  # the money earned by all the devices ruled to this contract during this round
        self._catalog.set(f"{self.name}.money_spent", 0)  # the money spent by all the devices ruled by this contract during this round

        self._catalog.set(f"{self.name}.energy_bought", 0)  # the energy bought by all the devices attached to this contract during this round
        self._catalog.set(f"{self.name}.energy_sold", 0)  # the energy sold by all the devices attached to this contract during this round

    # billing
    def _billing(self, quantity, agent_name):  # as the tariffs are not the same for selling or buying energy, this function redirects to the relevant function
        if quantity["energy_maximum"] > 0:  # if the maximal quantity of energy is positive, it means that the device asks for energy
            price = self._billing_buying(quantity["energy_maximum"])
        elif quantity["energy_maximum"] < 0:  # if the maximal quantity of energy is positive, it means that the device proposes energy
            price = self._billing_selling(quantity["energy_maximum"])
        else:  # if there is no need
            price = None  # no price is attributed
        self._user_billing(agent_name)

        return price

    def _billing_buying(self, quantity):  # the way of billing an agent buying energy. It is user-defined
        return None

    def _billing_selling(self, quantity):  # the way of billing an agent selling energy. It is user-defined
        return None

    def _user_billing(self, agent_name):  # here, the user can add specific operations
        pass

    # effort management
    def effort_modification(self, effort, agent_name):  # this function modifies effort according to the contract
        return effort  # if the function is not modified, it does not change the initial value

    # quantities management
    def quantity_modification(self, quantity, agent_name):  # this function modifies the priority according to the contract
        quantity["price"] = self._billing(quantity, agent_name)
        return quantity  # if the function is not modified, it does not change the initial value

    # ##########################################################################################
    # Utilities
    # ##########################################################################################

    @property
    def name(self):  # shortcut for read-only
        return self._name

    @property
    def nature(self):  # shortcut for read-only
        return self._nature

