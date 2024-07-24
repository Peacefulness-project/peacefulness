# This file, we create a strategy sub-class that will be used for the Deep Reinforcement Learning method.
# It updates the balance of each aggregator with the action/decision taken by the RL agent.
# The decision is taken at each iteration and it is translated with the strategy_interface.

# Imports
from src.common.Strategy import Strategy
from src.tools.DRL_Strategy_utilities import *
from src.common.World import World


class DeepReinforcementLearning(Strategy):
    world = World.ref_world

    def __init__(self):
        super().__init__("deep_reinforcement_learning_strategy", "The optimal energy management strategy that will be learned by the RL agent")

    # ##################################################################################################################
    # Dynamic behavior
    ####################################################################################################################

    def bottom_up_phase(self, aggregator: "Aggregator"):
        # TODO - at the moment the other information related to operational objectives except of economic, are not considered yet
        # TODO - Proposition 1 - on publie tout le besoin en énergie des agrégateurs a.k.a AlwaysSatisfied dans un seul message
        # Before publishing quantities and prices to the catalog, we gather relevant information to send to the RL agent
        # Namely, the data needed : energy prices, formalism variables representing the state of the MEG and forecasting
        quantities_and_prices = []
        message = aggregator.information_message()

        # Data on energy prices
        [min_price, max_price] = self._limit_prices(aggregator)  # thresholds of accepted energy prices
        # these two values are to be sent to the RL agent (part of the MEG state)
        buying_price, selling_price = determine_energy_prices(self, aggregator, min_price, max_price)
        self._catalog.add(f"{aggregator.name}.DRL_Strategy.energy_prices", {"buying_price": buying_price, "selling_price": selling_price})

        message["price"] = (buying_price + selling_price) / 2  # this value is the one published in the catalog

        # Data related to the formalism variables
        formalism_message = my_devices(self.world, aggregator)  # TODO à vérifier avec Timothé, le self.world ici !!!
        formalism_message = mutualize_formalism_message(formalism_message)  # TODO sous l'hypothèse de prendre les valeurs moyennes
        self._catalog.add(f"{aggregator.name}.DRL_Strategy.formalism_message", formalism_message)

        # Data on rigid energy consumption and production forecasting
        forecasting_message = self.call_to_forecast(aggregator)  # this dict is to be sent to the RL agent
        if forecasting_message is not None:
            self._catalog.add(f"{aggregator.name}.DRL_Strategy.forecasting_message", forecasting_message)

        # We define the min/max energy produced/consumed
        minimum_energy_consumed = 0  # the minimum quantity of energy needed to be consumed
        minimum_energy_produced = 0  # the minimum quantity of energy needed to be produced
        maximum_energy_consumed = 0  # the maximum quantity of energy needed to be consumed
        maximum_energy_produced = 0  # the maximum quantity of energy needed to be produced
        [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced] = self._limit_quantities(aggregator, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced)

        # The aggregator publishes its needs
        energy_difference = maximum_energy_consumed - maximum_energy_produced
        message["energy_minimum"] = energy_difference
        message["energy_nominal"] = energy_difference
        message["energy_maximum"] = energy_difference

        quantities_and_prices.append(message)
        quantities_and_prices = self._publish_needs(aggregator, quantities_and_prices)

        return quantities_and_prices

    def top_down_phase(self, aggregator: "Aggregator"):  # TODO pas besoin de récursion, car l'agrégateur s'en occupe ?
        # TODO voir comment traiter les conversions
        energy_bought_outside = 0  # the absolute value of energy bought outside
        energy_sold_outside = 0  # the absolute value of energy sold outside
        energy_bought_inside = 0  # the absolute value of energy bought inside
        energy_sold_inside = 0  # the absolute value of energy sold inside

        money_earned_outside = 0  # the absolute value of money earned outside
        money_spent_outside = 0  # the absolute value of money spent outside
        money_earned_inside = 0  # the absolute value of money earned inside
        money_spent_inside = 0  # the absolute value of money spent inside

        # we retrieve the energy accorded to each aggregator with the decision taken by the RL agent
        [energy_accorded_to_consumers, energy_accorded_to_producers, energy_accorded_to_storage, energy_accorded_to_exchange] = extract_decision(self.world.catalog.get("DRL_Strategy.decision_message"), aggregator)
        buying_price, selling_price = self.world.catalog.get(f"{aggregator.name}.DRL_Strategy.energy_prices").values()

        # Energy & prices balance of the aggregator
        # Exchange with outside (even superior/sub aggregators)
        energy_exchanges = sum(energy_accorded_to_exchange.values())
        if energy_exchanges < 0:  # the aggregator sold the energy to outside
            # if (energy_accorded_to_consumers + energy_accorded_to_producers + energy_accorded_to_storage) > 0:
            #     raise Exception(f"Attention, this {aggregator.name} could not balance itself !")
            energy_sold_outside = energy_exchanges
            money_earned_outside = - selling_price * energy_sold_outside
        else:  # the aggregator bought energy from outside
            energy_bought_outside = energy_exchanges
            money_spent_outside = buying_price * energy_bought_outside

        # Managed inside (only energy systems/devices directly managed by the aggregator)
        if energy_accorded_to_consumers > 0:  # energy is stored
            energy_bought_inside = energy_accorded_to_consumers + energy_accorded_to_storage
            energy_sold_inside = energy_accorded_to_producers
            money_spent_inside = energy_bought_inside * buying_price
            money_earned_inside = energy_sold_inside * selling_price
        else:  # energy from storage devices is extracted
            energy_bought_inside = energy_accorded_to_consumers
            energy_sold_inside = energy_accorded_to_producers + energy_accorded_to_storage
            money_spent_inside = energy_bought_inside * buying_price
            money_earned_inside = energy_sold_inside * selling_price

        # Energy distribution and billing
        # First we have to get the list of devices according to their use
        device_list = []
        consumers_list = []
        producers_list = []
        storage_list = []
        converters_list = []
        message = self.messages_manager.create_decision_message()
        for device_name in aggregator.devices:  # getting the list of all the devices directly managed by the aggregator
            device_list.append(self.world.catalog.get(device_name))

        for device in device_list:
            specific_message = device.messages_manager.get_information_message()
            if specific_message["type"] == "standard":
                Emax = self.world.catalog.get(f"{device.name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]
                if Emax > 0:  # the energy system consumes energy
                    consumers_list.append(device)
                else:  # the energy system produces energy
                    producers_list.append(device)
            elif specific_message["type"] == "storage":
                storage_list.append(device)
            elif specific_message["type"] == "converter":
                converters_list.append(device)

        # The energy is then distributed to the devices directly managed by the aggregator
        # Energy consumption
        consumption_difference = energy_accorded_to_consumers
        urgent_consumers = []
        non_urgent_consumers = []
        for consumer in consumers_list:
            Enom = self.world.catalog.get(f"{consumer.name}.{aggregator.nature.name}.energy_wanted")["energy_nominal"]
            Emax = self.world.catalog.get(f"{consumer.name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]
            if Enom == Emax:  # the energy demand is urgent
                urgent_consumers.append(consumer)
            else:  # the energy demand is not a priority
                non_urgent_consumers.append(consumer)
        for consumer in urgent_consumers:  # the priority devices get served all their needs
            Emax = self.world.catalog.get(f"{consumer.name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]
            Emin = self.world.catalog.get(f"{consumer.name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]
            if energy_accorded_to_consumers > Emax:
                message['quantity'] = Emax
                message["price"] = buying_price
            elif Emax > energy_accorded_to_consumers > Emin:
                message['quantity'] = Emin
                message["price"] = buying_price
            else:
                message['quantity'] = 0
                message["price"] = 0
            self.world.catalog.set(f"{consumer.name}.{aggregator.nature.name}.energy_accorded", message)
            energy_accorded_to_consumers -= message["quantity"]

        if energy_accorded_to_consumers > 0:  # if there is energy remaining to be consumed
            for consumer in non_urgent_consumers:  # the non-priority devices get to share the remaining energy
                Emin = self.world.catalog.get(f"{consumer.name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]
                if energy_accorded_to_consumers > Emin:
                    message['quantity'] = Emin
                    message["price"] = buying_price
                else:  # if the remaining energy is not enough
                    message['quantity'] = 0
                    message["price"] = 0
                self.world.catalog.set(f"{consumer.name}.{aggregator.nature.name}.energy_accorded", message)
                energy_accorded_to_consumers -= message["quantity"]
        maximum_energy_consumed = consumption_difference - energy_accorded_to_consumers

        # Energy production
        production_difference = energy_accorded_to_producers
        urgent_producers = []
        non_urgent_producers = []
        for producer in producers_list:
            Enom = self.world.catalog.get(f"{producer.name}.{aggregator.nature.name}.energy_wanted")["energy_nominal"]
            Emax = self.world.catalog.get(f"{producer.name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]
            if Enom == Emax:  # the energy demand is urgent
                urgent_producers.append(producer)
            else:  # the energy demand is not a priority
                non_urgent_producers.append(producer)
        for producer in urgent_producers:  # the priority devices get served all their needs
            Emax = self.world.catalog.get(f"{producer.name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]
            Emin = self.world.catalog.get(f"{producer.name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]
            if energy_accorded_to_producers < Emax:  # because of the negative signs
                message['quantity'] = Emax
                message["price"] = selling_price
            elif Emax < energy_accorded_to_producers < Emin:
                message['quantity'] = Emin
                message["price"] = selling_price
            else:
                message['quantity'] = 0
                message["price"] = 0
            self.world.catalog.set(f"{producer.name}.{aggregator.nature.name}.energy_accorded", message)
            energy_accorded_to_producers -= message["quantity"]

        if energy_accorded_to_producers < 0:  # if there is energy remaining to be consumed
            for producer in non_urgent_producers:  # the non-priority devices get to share the remaining energy
                Emin = self.world.catalog.get(f"{producer.name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]
                if energy_accorded_to_producers < Emin:
                    message['quantity'] = Emin
                    message["price"] = selling_price
                else:  # if the remaining energy is not enough
                    message['quantity'] = 0
                    message["price"] = 0
                self.world.catalog.set(f"{producer.name}.{aggregator.nature.name}.energy_accorded", message)
                energy_accorded_to_producers -= message["quantity"]
        maximum_energy_produced = production_difference - energy_accorded_to_producers

        # Energy storage
        if energy_accorded_to_storage < 0:  # on average the energy storage systems/devices want to sell energy
            for storage in storage_list:
                Emax = self.world.catalog.get(f"{storage.name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]
                Emin = self.world.catalog.get(f"{storage.name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]
                if Emax < 0:  # if the device wants to sell energy
                    Enom = self.world.catalog.get(f"{storage.name}.{aggregator.nature.name}.energy_wanted")["energy_nominal"]
                    if Enom == Emax:  # the energy demand is urgent
                        if energy_accorded_to_storage < Emax:
                            message["quantity"] = Emax
                            message["price"] = selling_price
                        elif Emax < energy_accorded_to_storage < Emin:
                            message["quantity"] = Emin
                            message["price"] = selling_price
                        else:
                            message["quantity"] = 0
                            message["price"] = 0
                    else:  # the energy demand is not urgent
                        if energy_accorded_to_storage < Emin:
                            message["quantity"] = Emin
                            message["price"] = selling_price
                        else:
                            message["quantity"] = 0
                            message["price"] = 0
                else:  # the device wants to buy energy, it will remain idle
                    message["quantity"] = 0
                    message["price"] = 0
                self.world.catalog.set(f"{storage.name}.{aggregator.nature.name}.energy_accorded", message)
                energy_accorded_to_storage -= message["quantity"]

        else:  # on average the energy storage systems/devices want to buy energy
            for storage in storage_list:
                Emax = self.world.catalog.get(f"{storage.name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]
                Emin = self.world.catalog.get(f"{storage.name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]
                if Emax > 0:  # if the device wants to buy energy
                    Enom = self.world.catalog.get(f"{storage.name}.{aggregator.nature.name}.energy_wanted")["energy_nominal"]
                    if Enom == Emax:  # the energy demand is urgent
                        if energy_accorded_to_storage > Emax:
                            message["quantity"] = Emax
                            message["price"] = buying_price
                        elif Emin < energy_accorded_to_storage < Emax:
                            message["quantity"] = Emin
                            message["price"] = buying_price
                        else:
                            message["quantity"] = 0
                            message["price"] = 0
                    else:  # the energy demand is not urgent
                        if energy_accorded_to_storage > Emin:
                            message["quantity"] = Emin
                            message["price"] = buying_price
                        else:
                            message["quantity"] = 0
                            message["price"] = 0
                else:  # the device wants to sell energy, it will remain idle
                    message["quantity"] = 0
                    message["price"] = 0
                self.world.catalog.set(f"{storage.name}.{aggregator.nature.name}.energy_accorded", message)
                energy_accorded_to_storage -= message["quantity"]

        # Energy conversion
        for converter in converters_list:
            Emax = self.world.catalog.get(f"{converter.name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]
            Enom = self.world.catalog.get(f"{converter.name}.{aggregator.nature.name}.energy_wanted")["energy_nominal"]
            Emin = self.world.catalog.get(f"{converter.name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]
            converter_efficiency = converter.get_efficiency()
            if converter_efficiency != 1:  # if the energy exchange is conducted with an energy conversion system/device
                if np.sign(Emax) == np.sign(energy_exchanges):  # the device does what the average of devices want
                    if Emax > 0:  # on average, the aggregator wants to buy energy from outside
                        if Emax == Enom:  # if the energy demand is urgent
                            if energy_exchanges > Emax:
                                message["quantity"] = Emax
                                message["price"] = buying_price
                            elif Emin < energy_exchanges < Emax:
                                message["quantity"] = Emin
                                message["price"] = buying_price
                            else:
                                message["quantity"] = 0
                                message["price"] = 0
                        else:  # if the energy demand is not urgent
                            if energy_exchanges > Emin:
                                message["quantity"] = Emin
                                message["price"] = buying_price
                            else:
                                message["quantity"] = 0
                                message["price"] = 0
                    else:  # on average, the aggregator wants to sell energy to outside
                        if Emax == Enom:  # if the energy demand is urgent
                            if energy_exchanges < Emax:
                                message["quantity"] = Emax
                                message["price"] = selling_price
                            elif Emax < energy_exchanges < Emin:
                                message["quantity"] = Emin
                                message["price"] = selling_price
                            else:
                                message["quantity"] = 0
                                message["price"] = 0
                        else:  # if the energy demand is not urgent
                            if energy_exchanges < Emin:
                                message["quantity"] = Emin
                                message["price"] = selling_price
                            else:
                                message["quantity"] = 0
                                message["price"] = 0
                else:  # the device does the opposite of what the average of devices want, it will remain idle
                    message["quantity"] = 0
                    message["price"] = 0

                self.world.catalog.set(f"{converter.name}.{aggregator.nature.name}.energy_accorded", message)
                energy_exchanges -= message["quantity"]

                converters_list.remove(converter)

        energy_left = energy_accorded_to_consumers + energy_accorded_to_producers + energy_accorded_to_storage + energy_exchanges

        # TODO confirmer la proposition de decision message avec Timothé
        # TODO valider avec Timothé la manière de calculer les energy bought/sold inside/outside et money earned/spent inside/outside
        self._update_balances(aggregator, energy_bought_inside, energy_bought_outside, energy_sold_inside, energy_sold_outside, money_spent_inside, money_spent_outside, money_earned_inside, money_earned_outside, maximum_energy_consumed, maximum_energy_produced)
