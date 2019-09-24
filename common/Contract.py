# Contract are objects used to enable/disable certain operations during the supervision
# They also serve to specify the way of billing the agents


class Contract:

    def __init__(self, name, nature, operations_allowed):
        self._name = name
        self._catalog = None
        self._nature = nature

        # in the following list are listed the operations allowed for each type of device
        # an empty list means that the supervisor has to accept
        # otherwise, the keywords are "shiftable", "adjustable" or "wipable"
        self._operations_allowed = {"non_controllable": operations_allowed[0],
                                    "shiftable": operations_allowed[1],
                                    "adjustable": operations_allowed[2],
                                    "storage": operations_allowed[3]
                                    }

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register(self, catalog):
        self._catalog = catalog

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    # billing
    def _billing(self, energy_amount, agent_name, nature):  # as the tariffs are not the same for selling or buying energy, this function redirects to the relevant function
        if energy_amount > 0:
            self._billing_buying(energy_amount, agent_name, nature)
        elif energy_amount < 0:
            self._billing_selling(energy_amount, agent_name, nature)

    def _billing_buying(self, energy_amount, agent_name, nature):  # the way of billing an agent buying energy. It is user-defined
        pass

    def _billing_selling(self, energy_amount, agent_name, nature):  # the way of billing an agent selling energy. It is user-defined
        pass

    # dissatisfaction management

    def dissatisfaction_modification(self, dissatisfaction):
        pass

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

    # ##########################################################################################
    # Utilities
    # ##########################################################################################

    @property
    def name(self):  # shortcut for read-only
        return self._name

    @property
    def nature(self):  # shortcut for read-only
        return self._nature

