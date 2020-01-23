# This contract is a contract in which the customer accepts to never be served.
from common.Contract import Contract
from tools.UserClassesDictionary import user_classes_dictionary
from tools.Utilities import sign


class TOUCurtailmentContract(Contract):

    def __init__(self, name, nature, parameters=None):
        super().__init__(name, nature)

        self.description = "A contract where the price is fixed over the time at a lower tariff than the TOU contract." \
                           "Meanwhile, the customer can be shifted and erased, which means she accepts not be served at all."

        self._parameters = [parameters["selling_price"], parameters["buying_price"]]

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):
        pass

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    # billing
    def _billing_buying(self, quantity):
        price = self._catalog.get(f"{self.nature.name}.buying_price_TOU") * 0.8   # getting the price per kW.h

        return price

    def _billing_selling(self, quantity):
        price = self._catalog.get(f"{self.nature.name}.selling_price_TOU") * 0.8   # getting the price per kW.h

        return price

    # quantity management
    def quantity_modification(self, quantity, agent_name):
        quantity["energy_minimum"] = 0  # set the minimal quantity of energy to 0
        quantity["energy_nominal"] = min(abs(quantity["energy_maximum"]*0.95), abs(quantity["energy_nominal"])) * sign(quantity["energy_maximum"])  # the abs() allows to manage both consumptions and productions
        # this contract forbids the quantity to be urgent
        # it means that the devices will never be sure to be served

        quantity["price"] = self._billing(quantity, agent_name)

        return quantity


user_classes_dictionary[f"{TOUCurtailmentContract.__name__}"] = TOUCurtailmentContract


