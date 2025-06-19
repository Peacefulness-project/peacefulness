# The goal of this strategy is to simulate a market
from src.common.Strategy import Strategy, get_price
from typing import List, Dict


class MarketSimulator(Strategy):

    def __init__(self):
        super().__init__("market_simulator_strategy", "This class is a mother class for simulating an energy market. It should never be implemented directly")

        self._quantities_exchanged_internally = dict()  # this dict contains the quantities exchanged internally

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _matching_algorithm(self, sorted_demands: List, sorted_offers: List, min_price: float, max_price: float, maximum_energy_produced: float, maximum_energy_consumed: float) -> Dict:
        pass

    def top_down_phase(self, aggregator: "Aggregator"):  # after having exchanged with the exterior, the aggregator distributes energy
        minimum_energy_consumed = 0  # the minimum quantity of energy needed to be consumed
        minimum_energy_produced = 0  # the minimum quantity of energy needed to be produced
        maximum_energy_consumed = 0  # the maximum quantity of energy needed to be consumed
        maximum_energy_produced = 0  # the maximum quantity of energy needed to be produced
        maximum_energy_charge = 0  # the maximum quantity of energy acceptable by storage charge
        maximum_energy_discharge = 0  # the maximum quantity of energy available from storage discharge

        [min_price, max_price] = self._limit_prices(aggregator)  # min and max prices allowed

        # ##########################################################################################
        # calculus of the minimum and maximum quantities of energy involved in the aggregator

        [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, maximum_energy_charge, maximum_energy_discharge] = self._limit_quantities(aggregator, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, maximum_energy_charge, maximum_energy_discharge)

        # formulation of needs
        [sorted_demands, sorted_offers, sorted_storage] = self._separe_quantities(aggregator)

        sorted_demands, sorted_offers = self._price_limiting(min_price, max_price, sorted_demands, sorted_offers)

        # ##########################################################################################
        # balance of energy available
        decision_messages = self._matching_algorithm(sorted_demands, sorted_offers, min_price, max_price, maximum_energy_produced, maximum_energy_consumed)  # algorithm that determines the quantities affected to each subaggregator

        energy_bought_inside, energy_sold_inside, money_earned_inside, money_spent_inside = self._transmit_decisions(decision_messages, aggregator)

        # ##########################################################################################
        # updates the balances
        self._update_balances(aggregator, energy_bought_inside, 0, energy_sold_inside, 0, money_spent_inside, 0, money_earned_inside, 0, maximum_energy_consumed, maximum_energy_produced)

    def _price_limiting(self, min_price: float, max_price: float, sorted_demands: List, sorted_offers: List):
        for message in sorted_demands:
            price = message["price"]
            price = min(max(price, min_price), max_price)  # the price is bounded between the minimum and the maximum price
            message["price"] = price
        for message in sorted_offers:
            price = message["price"]
            price = min(max(price, min_price), max_price)  # the price is bounded between the minimum and the maximum price
            message["price"] = price
        return sorted_demands, sorted_offers

    def _transmit_decisions(self, decision_messages: Dict, aggregator: "Aggregator"):
        money_earned_inside = 0  # money earned by selling energy to the subaggregator
        money_spent_inside = 0
        energy_sold_inside = 0  # the absolute value of energy sold inside
        energy_bought_inside = 0

        if len(decision_messages) >= 1:  # if there are offers
            for name, message in decision_messages.items():
                # name = decision_messages[i]["name"]
                # energy = decision_messages[i]["quantity"]  # the quantity of energy needed
                # price = decision_messages[i]["price"]  # the price of energy
                #
                # message = self._create_decision_message()
                energy = message["quantity"]
                price = message["price"]

                if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                else:  # if it is a device
                    quantities_given = message

                self._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

                if energy > 0:
                    money_earned_inside += energy * price  # money earned by selling energy to the subaggregator
                    energy_sold_inside += energy  # the absolute value of energy sold inside
                elif energy < 0:
                    money_spent_inside -= energy * price  # money earned by selling energy to the subaggregator
                    energy_bought_inside -= energy  # the absolute value of energy sold inside

        return energy_bought_inside, energy_sold_inside, money_earned_inside, money_spent_inside

