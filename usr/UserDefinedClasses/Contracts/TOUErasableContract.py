# This contract is a contract in which the customer accepts to never be served.
from common.Contract import Contract
from tools.UserClassesDictionary import user_classes_dictionary


class TOUErasableContract(Contract):

    def __init__(self, name, nature, parameters=None):
        super().__init__(name, nature)

        self.description = "A contract where the price is fixed over the time at a lower tariff than the TOU contract." \
                           "Meanwhile, the customer can be shifted and erased, which means she accepts not be served at all."

        self._parameters = [parameters["selling_price"], parameters["buying_price"]]

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):
        self._catalog.set(f"{self.name}.{self.nature}.buying_price", self._parameters[0])  # the price paid to buy energy of a given nature with this contract
        self._catalog.set(f"{self.name}.{self.nature}.selling_price", self._parameters[1])  # the price received by selling energy  of a given nature with this contract

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    # billing
    def _billing_buying(self, quantity):
        price = self._catalog.get(f"{self.name}.{self.nature.name}.buying_price")  # getting the price per kW.h

        return price

    def _billing_selling(self, quantity):
        price = self._catalog.get(f"{self.name}.{self.nature.name}.selling_price")  # getting the price per kW.h

        return price

    # quantity management
    def quantity_modification(self, quantity, agent_name):
        quantity[0][0] = 0  # set the minimal quantity of energy to 0
        quantity[0][1] = min(quantity[0][1]*0.95, quantity[0][2])  # this contract forbids the quantity to be urgent
        # it means that the devices will never be sure to be served

        quantity[1] = self._billing(quantity[0], agent_name)

        return quantity


user_classes_dictionary[f"{TOUErasableContract.__name__}"] = TOUErasableContract

