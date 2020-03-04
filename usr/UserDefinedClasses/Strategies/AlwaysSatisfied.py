# This sheet describes a strategy always wanting to buy all the energy lacking and to sell all the energy available
# It corresponds to the current "strategy" in France and can be used as a reference.
from common.Strategy import Strategy
from tools.UserClassesDictionary import user_classes_dictionary
from tools.Utilities import sign
from common.Strategy import SupervisorException

from math import inf


class AlwaysSatisfied(Strategy):

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def ascendant_phase(self, aggregator):  # before communicating with the exterior, the aggregator makes its local balances
        energy_difference = 0  # this energy is the difference between the energy consumed and produced locally

        # getting back the needs for every device --> standard probably
        for device_name in aggregator.devices:
            Emax = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]  # maximal quantity of energy wanted by the device

            energy_difference += Emax  # incrementing the total
            aggregator.quantities[device_name] = [Emax, sign(Emax) * inf, 0, 0]  # the local quantities are updated in the aggregator dedicated dictionary

        for subaggregator in aggregator.subaggregators:
            managed_aggregator_quantities = self._catalog.get(f"{subaggregator.name}.quantities_asked")  # couples prices/quantities asked by the managed aggregators
            i = 0  # an arbitrary number given to couples price/quantities
            for element in managed_aggregator_quantities:
                energy_difference += element[0]
                aggregator.quantities[f"{subaggregator.name}_lot_{i}"] = [element[0], element[1], 0, 0]
                i += 1

        quantities_and_prices = [[energy_difference, sign(energy_difference)*inf]]  # wants to satisfy everyone, regardless the price (i.e sells even at -inf and buys even at +inf)

        self._publish_needs(aggregator, quantities_and_prices)

    def distribute_remote_energy(self, aggregator):  # after having exchanged with the exterior, the aggregator distributes the energy among its devices and aggregators
        quantities_asked = {"bought": 0, "sold": 0}
        quantities_given = {"bought": 0, "sold": 0}

        energy_bought_outside = 0  # the absolute value of energy bought outside
        energy_sold_outside = 0  # the absolute value of energy sold outside
        energy_bought_inside = 0  # the absolute value of energy bought inside
        energy_sold_inside = 0  # the absolute value of energy sold inside

        money_earned_outside = 0  # the absolute value of money earned outside
        money_spent_outside = 0  # the absolute value of money spent outside
        money_earned_inside = 0  # the absolute value of money earned inside
        money_spent_inside = 0  # the absolute value of money spent inside

        [min_price, max_price] = self._limit_prices(aggregator)  # min and max prices allowed

        # counting the offers and the demands at its own level
        # what was asked
        for couple in self._catalog.get(f"{aggregator.name}.quantities_asked"):
            if couple[0] > 0:  # energy the aggregator wanted to buy
                quantities_asked["bought"] += couple[0]  # the quantity of energy asked the aggregator wanted to buy
            elif couple[0] < 0:  # energy the aggregator wanted to sell
                quantities_asked["sold"] += couple[0]  # the quantity of energy asked the aggregator wanted to sell

        # what is given
        for couple in self._catalog.get(f"{aggregator.name}.quantities_given"):
            if couple[0] > 0:  # energy bought by the aggregator
                quantities_given["bought"] += couple[0]  # the quantity of energy sold to the aggregator
                couple[1] = min(couple[1], max_price)  # maximum price is artificially limited

                # making balances
                # energy bought
                energy_bought_outside += couple[0]  # the absolute value of energy bought outside
                money_spent_outside += couple[0] * couple[1]  # the absolute value of money spent outside

            elif couple[0] < 0:  # energy sold by the aggregator
                quantities_given["sold"] += couple[0]  # the quantity of energy bought by the aggregator
                couple[1] = max(couple[1], min_price)  # minimum price is artificially limited

                # making balances
                # energy sold
                energy_sold_outside -= couple[0]  # the absolute value of energy sold outside
                money_earned_outside -= couple[0] * couple[1]  # the absolute value of money earned outside

        # energy distribution and billing
        if quantities_given == quantities_asked:  # if the aggregator got what it wanted

            # quantities concerning devices
            for device_name in aggregator.devices:
                energy = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]  # the maximum quantity of energy asked
                price = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["price"]  # the price of the energy asked

                # balances
                if energy > 0:  # energy bought
                    price = min(price, max_price)

                    self._catalog.set(f"{device_name}.{aggregator.nature.name}.energy_accorded", {"quantity": energy, "price": price})

                    money_earned_inside += energy * price  # money earned by selling energy to the device
                    energy_sold_inside += energy  # the absolute value of energy sold inside
                elif energy < 0:  # energy sold
                    price = max(price, min_price)

                    self._catalog.set(f"{device_name}.{aggregator.nature.name}.energy_accorded", {"quantity": energy, "price": price})

                    money_spent_inside -= energy * price  # money spent by buying energy from the device
                    energy_bought_inside -= energy  # the absolute value of energy bought inside

            # quantities concerning subaggregators
            for subaggregator in aggregator.subaggregators:  # quantities concerning aggregators
                quantities_and_prices = self._catalog.get(f"{subaggregator.name}.quantities_asked")
                self._catalog.set(f"{subaggregator.name}.quantities_given", quantities_and_prices)

                # balances
                for couple in quantities_and_prices:  # for each couple energy/price
                    if couple[0] > 0:  # energy bought
                        couple[1] = min(couple[1], max_price)  # maximum price is artificially limited

                        money_earned_inside += couple[0] * couple[1]  # money earned by selling energy to the subaggregator
                        energy_sold_inside += couple[0]  # the absolute value of energy sold inside
                    elif couple[0] < 0:  # energy sold
                        couple[1] = max(couple[1], min_price)  # minimum price is artificially limited

                        money_spent_inside -= couple[0] * couple[1]  # money spent by buying energy from the subaggregator
                        energy_bought_inside -= couple[0]  # the absolute value of energy bought inside
        else:
            # as we suppose that there is always a grid able to buy/sell an infinite quantity of energy, we souldn't be in this case
            raise SupervisorException("An always satisfied supervision supposes the access to an infinite provider/consumer")

        # updates the balances
        self._catalog.set(f"{aggregator.name}.energy_bought", {"inside": energy_bought_inside, "outside": energy_bought_outside})
        self._catalog.set(f"{aggregator.name}.energy_sold", {"inside": energy_sold_inside, "outside": energy_sold_outside})

        self._catalog.set(f"{aggregator.name}.money_spent", {"inside": money_spent_inside, "outside": money_spent_outside})
        self._catalog.set(f"{aggregator.name}.money_earned", {"inside": money_earned_inside, "outside": money_earned_outside})


user_classes_dictionary[f"{AlwaysSatisfied.__name__}"] = AlwaysSatisfied




