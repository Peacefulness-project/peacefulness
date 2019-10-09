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

    def _register(self, catalog):
        self._catalog = catalog

        self._user_register()

    def _user_register(self):
        pass

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

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

    # dissatisfaction management
    def dissatisfaction_modification(self, dissatisfaction):  # this function modifies dissatisfaction according to the contract
        return dissatisfaction  # If the function is not modified, it does not change the initial value

    # def non_controllable_dissatisfaction(self, agent_name, device_name, natures):  # the function handling dissatisfaction for non controllable devices. It is user-defined
    #     pass
    #
    # def shiftable_dissatisfaction(self, agent_name, device_name, natures):  # the function handling dissatisfaction for shiftable devices. It is user-defined
    #     pass
    #
    # def adjustable_dissatisfaction(self, agent_name, device_name, natures):  # the function handling dissatisfaction for adjustable devices. It is user-defined
    #     pass
    #
    # def storage_dissatisfaction(self, agent_name, device_name, natures):  # the function handling dissatisfaction for storage devices. It is user-defined
    #     pass

    # priority management
    def priority_modification(self, priority):  # this function modifies the priority according to the contract
        return priority  # If the function is not modified, it does not change the initial value

    # ##########################################################################################
    # Utilities
    # ##########################################################################################

    @property
    def name(self):  # shortcut for read-only
        return self._name

    @property
    def nature(self):  # shortcut for read-only
        return self._nature

