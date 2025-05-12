# The goal of this strategy is to simulate a market
from lib.Subclasses.Strategy.MarketSimulator.MarketSimulator import MarketSimulator
from typing import List, Dict


class EquilibriumPriceMarket(MarketSimulator):

    def __init__(self):
        super().__init__()

        self._quantities_exchanged_internally = dict()  # this dict contains the quantities exchanged internally

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _matching_algorithm(self, sorted_demands: List, sorted_offers: List, min_price: float, max_price: float, maximum_energy_produced: float, maximum_energy_consumed: float) -> Dict:
        mixed_messages = sorted_demands + sorted_offers
        decision_messages = {message["name"]: {"quantity": 0, "price": 0} for message in mixed_messages}

        # the minimum to keep available to satisfy the urgent needs
        if maximum_energy_consumed > maximum_energy_produced:  # if there is more consumption
            energy_available = maximum_energy_produced
        else:
            energy_available = maximum_energy_consumed

        i = 0
        j = 0
        exchange_price = 0  # in this cas, there is only one price affected to all exchanges
        print(sorted_offers, sorted_demands)
        while i < len(sorted_demands) and j < len(sorted_offers) and energy_available:
            buying_price = sorted_demands[i]["price"]
            selling_price = sorted_offers[j]["price"]

            if buying_price >= selling_price:
                consumer_name = sorted_demands[i]["name"]
                producer_name = sorted_offers[j]["name"]

                if sorted_demands[i]["quantity"] > - sorted_offers[j]["quantity"]:  # if the producer cannot serve totally
                    quantity_served = min(-sorted_offers[j]["quantity"], energy_available)
                    sorted_demands[i]["quantity"] -= quantity_served  # the part served
                    sorted_offers[j]["quantity"] += quantity_served
                    j += 1  # next producer
                    energy_available -= quantity_served

                    # decision saving
                    decision_messages[consumer_name]["quantity"] += quantity_served
                    decision_messages[producer_name]["quantity"] -= quantity_served
                    exchange_price = buying_price

                else:  # if the producer can serve totally
                    quantity_served = min(sorted_demands[i]["quantity"], energy_available)
                    sorted_demands[i]["quantity"] -= quantity_served  # the part served
                    sorted_offers[j]["quantity"] += quantity_served
                    i += 1  # next consumer
                    energy_available -= quantity_served

                    # decision saving
                    decision_messages[consumer_name]["quantity"] += quantity_served
                    decision_messages[producer_name]["quantity"] -= quantity_served
                    exchange_price = selling_price
            else:
                break

        for decision_message in decision_messages.values():
            decision_message["price"] = exchange_price
        # print(decision_messages)

        return decision_messages

