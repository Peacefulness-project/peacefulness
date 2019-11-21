# Contract are objects used to enable/disable certain operations during the supervision
# They also serve to specify the way of billing the agents


class Contract:

    def __init__(self, name, nature, parameters=None):
        self._name = name
        self._catalog = None
        self._nature = nature

        self.description = ""  # a brief description of the contract

        # parameters is an optional dictionary which stores additional information needed by user-defined classes
        # putting these information there allow them to be saved/loaded via world method
        if parameters:
            self._parameters = parameters
        else:  # if there are no parameters
            self._parameters = {}  # they are put in an empty dictionary

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register(self, catalog):  # add a catalog and create relevant entries
        self._catalog = catalog

        self._catalog.add(f"{self.name}.{self.nature.name}.buying_price", None)  # the price paid to buy energy of a given nature with this contract
        self._catalog.add(f"{self.name}.{self.nature.name}.selling_price", None)  # the price received by selling energy  of a given nature with this contract

        self._user_register()

        # Creation of specific entries
        self._catalog.add(f"{self.name}.money_earned", 0)  # the money earned by all the devices ruled to this contract during this round
        self._catalog.add(f"{self.name}.money_spent"), 0  # the money spent by all the devices ruled by this contract during this round

        self._catalog.add(f"{self.name}.energy_bought", 0)  # the energy bought by all the devices attached to this contract during this round
        self._catalog.add(f"{self.name}.energy_sold", 0)  # the energy sold by all the devices attached to this contract during this round

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
    def _billing(self, energy_amount, agent_name):  # as the tariffs are not the same for selling or buying energy, this function redirects to the relevant function
        if energy_amount > 0:
            self._billing_buying(energy_amount, agent_name)
        elif energy_amount < 0:
            self._billing_selling(energy_amount, agent_name)
        self._user_billing(agent_name)

    def _billing_buying(self, energy_amount, agent_name):  # the way of billing an agent buying energy. It is user-defined
        pass

    def _billing_selling(self, energy_amount, agent_name):  # the way of billing an agent selling energy. It is user-defined
        pass

    def _user_billing(self, agent_name):  # here, the user can add specific operations
        pass

    # effort management
    def effort_modification(self, effort):  # this function modifies effort according to the contract
        return effort  # of the function is not modified, it does not change the initial value

    # priority management
    def quantity_modification(self, quantity):  # this function modifies the priority according to the contract
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

