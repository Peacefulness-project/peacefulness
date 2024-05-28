# This file, we create a strategy sub-class that will be used for the Deep Reinforcement Learning method.
# It updates the balance of each aggregator with the action/decision taken by the RL agent.
# The decision is taken at each iteration and it is translated with the strategy_interface.

# Imports
from src.common.Strategy import Strategy
from src.tools.Utilities import into_list
from typing import Callable


class DeepReinforcementLearning(Strategy):
    def __init__(self, ascendant_interface: Callable, descendant_interface: Callable):
        super().__init__("deep_reinforcement_learning_strategy", "The optimal energy management strategy will be learned by the RL agent")
        self.interface = [ascendant_interface, descendant_interface]  # this ensures communication between peacefulness and the DRL code

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def bottom_up_phase(self, aggregator: "Aggregator"):
        # TODO à modifier
        # The information to be communicated to the DRL method in order to define the state of the grid
        prediction = self.call_to_forecast(aggregator)
        [min_price, max_price] = self._limit_prices(aggregator)
        formalism = [{}]
        device_wanted_energy = [{}]
        for device in aggregator.devices:
            device_wanted_energy = self._catalog.get(f"{device}.{aggregator.nature.name}.energy_wanted")
            formalism = device._create_message()

        self.interface[0](min_price, max_price, prediction, formalism, device_wanted_energy)

        quantities_and_prices = [aggregator.information_message()]
        quantities_and_prices = self._publish_needs(aggregator, quantities_and_prices)

        return quantities_and_prices

    def top_down_phase(self, aggregator: "Aggregator"):
        # TODO voir comment traiter les conversions
        energy_bought_outside = 0  # the absolute value of energy bought outside
        energy_sold_outside = 0  # the absolute value of energy sold outside
        energy_bought_inside = 0  # the absolute value of energy bought inside
        energy_sold_inside = 0  # the absolute value of energy sold inside

        money_earned_outside = 0  # the absolute value of money earned outside
        money_spent_outside = 0  # the absolute value of money spent outside
        money_earned_inside = 0  # the absolute value of money earned inside
        money_spent_inside = 0  # the absolute value of money spent inside

        # we retrieve the energy accorded to each independent aggregator with the decision taken by the RL agent
        [energy_accorded_to_consumers, energy_accorded_to_producers, energy_accorded_to_storage,energy_accorded_to_exchange] = self.interface[1](aggregator.name)

        consumption_energy = energy_accorded_to_consumers.values()[0]
        consumption_price = energy_accorded_to_consumers.values()[1]
        production_energy = energy_accorded_to_producers.values()[0]
        production_price = energy_accorded_to_producers.values()[1]
        storage_energy = energy_accorded_to_storage.values()[0]
        storage_price = energy_accorded_to_storage.values()[1]
        exchange_energy = energy_accorded_to_exchange.values()[0]
        exchange_price = energy_accorded_to_exchange.values()[1]

        if exchange_energy < 0:  # the aggregator sold the energy to outside
            energy_sold_outside = exchange_energy
            money_earned_outside = - exchange_price * exchange_energy
        else:  # the aggregator bought energy from outside
            energy_bought_outside = exchange_energy
            money_spent_outside = exchange_price * exchange_energy

        consumers_list = into_list(energy_accorded_to_consumers.keys())  # list of all the energy consumers managed by the aggregator (even if they are managed by a subaggregator)
        producers_list = into_list(energy_accorded_to_producers.keys())  # list of all the energy producers managed by the aggregator (even if they are managed by a subaggregator)
        storage_devices = into_list(energy_accorded_to_storage.keys())  # list of all the energy storage devices managed by the aggregator (even if they are managed by a subaggregator)

        # Quantities and prices concerning devices directly managed
        aggregator_consumers = []
        aggregator_producers = []
        aggregator_storage = []
        for device in aggregator.devices:
            for name in consumers_list:
                if device.name in name:
                    aggregator_consumers.append(device)
            for name in producers_list:
                if device.name in name:
                    aggregator_producers.append(device)
            for name in storage_devices:
                if device.name in name:
                    aggregator_storage.append(device)

        for consumer in aggregator_consumers:
            message = self._create_decision_message()
            need = self._catalog.get(f"{consumer}.{aggregator.nature.name}.energy_wanted")
            message["quantity"] = min(consumption_energy * len(aggregator_consumers)/len(consumers_list), need["energy_maximum"])
            message["price"] = max(consumption_price, need["price"])
            energy_bought_inside += message["quantity"]
            money_spent_inside += message["quantity"] * message["price"]
            self._catalog.set(f"{consumer}.{aggregator.nature.name}.energy_accorded", message)
        for producer in aggregator_producers:
            message = self._create_decision_message()
            need = self._catalog.get(f"{producer}.{aggregator.nature.name}.energy_wanted")
            message["quantity"] = min(production_energy * len(aggregator_producers)/len(producers_list), need["energy_maximum"])
            message["price"] = min(production_price, need["price"])
            energy_sold_inside += message["quantity"]
            money_earned_inside += message["quantity"] * message["price"]
            self._catalog.set(f"{producer}.{aggregator.nature.name}.energy_accorded", message)
        for storage in aggregator_storage:
            message = self._create_decision_message()
            need = self._catalog.get(f"{storage}.{aggregator.nature.name}.energy_wanted")
            message["quantity"] = min(storage_energy * len(aggregator_storage)/len(storage_devices), need["energy_maximum"])
            if message["quantity"] < 0:  # the device wants to sell energy
                message["price"] = min(storage_price, need["price"])
                energy_sold_inside += message["quantity"]
                money_earned_inside += message["quantity"] * message["price"]
            else:  # the device wants to buy energy
                message["price"] = max(storage_price, need["price"])
                energy_bought_inside += message["quantity"]
                money_spent_inside += message["quantity"] * message["price"]
            self._catalog.set(f"{storage}.{aggregator.nature.name}.energy_accorded", message)

        # Quantities and prices concerning the subaggregators
        for subaggregator in aggregator.subaggregators:
            message = self._create_decision_message()
            quantities_accorded = []

            need = self._catalog.get(f"{subaggregator.name}.{aggregator.nature.name}.energy_wanted")

            subaggregator_consumers = []
            subaggregator_producers = []
            subaggregator_storage = []
            for name in consumers_list:
                if subaggregator.name in name:
                    subaggregator_consumers.append(subaggregator.name)
            for name in producers_list:
                if subaggregator.name in name:
                    subaggregator_producers.append(subaggregator.name)
            for name in storage_devices:
                if subaggregator.name in name:
                    subaggregator_storage.append(subaggregator.name)

            energy_to_consume = min(consumption_energy * len(subaggregator_consumers)/len(consumers_list), need["consumption"]["energy_maximum"])
            price_to_consume = max(consumption_price, need["consumption"]["price"])
            energy_to_produce = min(production_energy * len(subaggregator_producers)/len(producers_list), need["production"]["energy_maximum"])
            price_to_produce = min(production_price, need["production"]["price"])
            energy_to_store = min(storage_energy * len(subaggregator_storage)/len(storage_devices), need["storage"]["energy_maximum"])
            if energy_to_store < 0:  # the subaggregator with energy storage facilities sells energy
                price_to_storage = min(storage_price, need["storage"]["price"])
            else:  # the subaggregator with energy facilities buys energy
                price_to_storage = max(storage_price, need["storage"]["price"])

            # TODO confirmer la proposition de decision message avec Timothé
            message["quantity"]["consumption"] = energy_to_consume
            message["price"]["consumption"] = price_to_consume
            message["quantity"]["production"] = energy_to_produce
            message["price"]["production"] = price_to_produce
            message["quantity"]["storage"] = energy_to_store
            message["price"]["storage"] = price_to_storage
            quantities_accorded.append(message)

            if message["quantity"]["storage"] < 0:  # the subaggregator with energy storage facilities sells energy
                energy_bought_inside += message["quantity"]["consumption"]
                energy_sold_inside += message["quantity"]["production"] + message["quantity"]["storage"]
                money_spent_inside += message["quantity"]["consumption"] * message["price"]["consumption"]
                money_earned_inside += message["quantity"]["production"] * message["price"]["production"] + message["quantity"]["storage"] * message["price"]["storage"]
            else:  # the subaggregator with energy facilities buys energy
                energy_bought_inside += message["quantity"]["consumption"] + message["quantity"]["storage"]
                energy_sold_inside += message["quantity"]["production"]
                money_spent_inside += message["quantity"]["consumption"] * message["price"]["consumption"] + message["quantity"]["storage"] * message["price"]["storage"]
                money_earned_inside += message["quantity"]["production"] * message["price"]["production"]

            self._catalog.set(f"{subaggregator.name}.{aggregator.nature.name}.energy_accorded", quantities_accorded)
        # TODO valider avec Timothé la manière de calculer les energy bought/sold inside/outside et money earned/spent inside/outside
        self._update_balances(aggregator, energy_bought_inside, energy_bought_outside, energy_sold_inside, energy_sold_outside, money_spent_inside, money_spent_outside, money_earned_inside, money_earned_outside, energy_sold_inside, energy_bought_inside)
