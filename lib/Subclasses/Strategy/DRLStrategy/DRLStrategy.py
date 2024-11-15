# This file, we create a strategy sub-class that will be used for the Deep Reinforcement Learning method.
# It updates the balance of each aggregator with the action/decision taken by the RL agent.
# The decision is taken at each iteration and it is translated with the strategy_interface.

# Imports
from src.common.Strategy import Strategy
from src.tools.DRL_Strategy_utilities import *
from interface_peacefulness import *


class DeepReinforcementLearning(Strategy):

    def __init__(self, agent: "A3C_agent"):
        super().__init__("deep_reinforcement_learning_strategy", "The optimal energy management strategy that will be learned by the RL agent")
        self.agent = agent
        self.counter = 0  # will be used to send and receive information from the RL agent
        self.scope = None  # list of aggregators managed by this strategy in particular

    # ##################################################################################################################
    # Dynamic behavior
    ####################################################################################################################

    def bottom_up_phase(self, aggregator):
        # TODO - at the moment the other information related to operational objectives except of economic, are not considered yet
        # TODO - Proposition 1 - on publie tout le besoin en énergie des agrégateurs a.k.a AlwaysSatisfied dans un seul message
        # Before publishing quantities and prices to the catalog, we gather relevant information to send to the RL agent
        # Namely, the data needed : energy prices, formalism variables representing the state of the MEG and forecasting
        self.scope = self._catalog.get(f"DRL_Strategy.strategy_scope")
        quantities_and_prices = []
        message = {**self._create_information_message()}

        # Data on energy prices
        [min_price, max_price] = self._limit_prices(aggregator)  # thresholds of accepted energy prices
        # these two values are to be sent to the RL agent (part of the MEG state)
        buying_price, selling_price = determine_energy_prices(self._catalog, aggregator, min_price, max_price)
        if f"{aggregator.name}.DRL_Strategy.energy_prices" not in self._catalog.keys:
            self._catalog.add(f"{aggregator.name}.DRL_Strategy.energy_prices", {"buying_price": buying_price, "selling_price": selling_price})
        else:
            self._catalog.set(f"{aggregator.name}.DRL_Strategy.energy_prices", {"buying_price": buying_price, "selling_price": selling_price})

        message["price"] = (buying_price + selling_price) / 2  # this value is the one published in the catalog

        # Data related to the formalism variables and lateral energy exchanges (with energy conversion systems)
        direct_exchanges = {}
        formalism_message, converter_message = my_devices(self._catalog, aggregator)
        formalism_message = mutualize_formalism_message(formalism_message)  # TODO sous l'hypothèse de prendre les valeurs moyennes

        if f"{aggregator.name}.DRL_Strategy.formalism_message" not in self._catalog.keys:
            self._catalog.add(f"{aggregator.name}.DRL_Strategy.formalism_message", formalism_message)
        else:
            self._catalog.set(f"{aggregator.name}.DRL_Strategy.formalism_message", formalism_message)
        if f"{aggregator.name}.DRL_Strategy.converter_message" not in self._catalog.keys:
            self._catalog.add(f"{aggregator.name}.DRL_Strategy.converter_message", converter_message[aggregator.name])
        else:
            self._catalog.set(f"{aggregator.name}.DRL_Strategy.converter_message", converter_message[aggregator.name])

        # Data on rigid energy consumption and production forecasting
        forecasting_message = self.call_to_forecast(aggregator)  # this dict is to be sent to the RL agent
        if forecasting_message is not None:
            if f"{aggregator.name}.DRL_Strategy.forecasting_message" not in self._catalog.keys:
                self._catalog.add(f"{aggregator.name}.DRL_Strategy.forecasting_message", forecasting_message)
            else:
                self._catalog.set(f"{aggregator.name}.DRL_Strategy.forecasting_message", forecasting_message)

        # We define the min/max energy produced/consumed (todo - voir si ça marche)
        message["energy_minimum"] = - aggregator.capacity["selling"]
        message["energy_nominal"] = 0.0
        message["energy_maximum"] = aggregator.capacity["buying"]
        # minimum_energy_consumed = 0  # the minimum quantity of energy needed to be consumed
        # minimum_energy_produced = 0  # the minimum quantity of energy needed to be produced
        # maximum_energy_consumed = 0  # the maximum quantity of energy needed to be consumed
        # maximum_energy_produced = 0  # the maximum quantity of energy needed to be produced
        # [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced] = self._limit_quantities(aggregator, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced)
        #
        # # The aggregator publishes its needs
        # energy_difference = maximum_energy_consumed - maximum_energy_produced
        # message["energy_minimum"] = energy_difference
        # message["energy_nominal"] = energy_difference
        # message["energy_maximum"] = energy_difference

        # TODO verify this proposal with Timothé
        if aggregator.superior:
            if aggregator.nature.name == aggregator.superior.nature.name:
                message["energy_minimum"] = message["energy_minimum"] * aggregator.efficiency
                message["energy_nominal"] = message["energy_nominal"] * aggregator.efficiency
                message["energy_maximum"] = message["energy_maximum"] * aggregator.efficiency
                if f"Energy asked from {aggregator.name} to {aggregator.superior.name}" not in self._catalog.keys:
                    self._catalog.add(f"Energy asked from {aggregator.name} to {aggregator.superior.name}", message)
                else:
                    self._catalog.set(f"Energy asked from {aggregator.name} to {aggregator.superior.name}", message)

        # Data related to the hierarchical energy exchanges (between subaggregators and superior)
        for subaggregator in aggregator.subaggregators:
            direct_exchanges = {aggregator.name: {subaggregator.name: {}}}
            if subaggregator.nature.name == aggregator.nature.name:
                if f"Energy asked from {subaggregator.name} to {aggregator.name}" in self._catalog.keys:
                    direct_exchanges[aggregator.name][subaggregator.name] = self._catalog.get(f"Energy asked from {subaggregator.name} to {aggregator.name}")
                else:
                    direct_exchanges[aggregator.name][subaggregator.name] = self._catalog.get(f"{subaggregator.name}.{aggregator.nature.name}.energy_wanted")
        if aggregator.superior:
            direct_exchanges = {**direct_exchanges, **{aggregator.superior.name: {aggregator.name: {}}}}
            if aggregator.nature.name == aggregator.superior.nature.name:
                direct_exchanges[aggregator.superior.name][aggregator.name] = self._catalog.get(f"Energy asked from {aggregator.name} to {aggregator.superior.name}")
        if direct_exchanges:
            if aggregator.name in direct_exchanges:
                if f"{aggregator.name}.DRL_Strategy.direct_energy_exchanges" not in self._catalog.keys:
                    self._catalog.add(f"{aggregator.name}.DRL_Strategy.direct_energy_exchanges", direct_exchanges[aggregator.name])
                else:
                    self._catalog.set(f"{aggregator.name}.DRL_Strategy.direct_energy_exchanges", direct_exchanges[aggregator.name])
            else:
                if f"{aggregator.name}.DRL_Strategy.direct_energy_exchanges" not in self._catalog.keys:
                    self._catalog.add(f"{aggregator.name}.DRL_Strategy.direct_energy_exchanges", direct_exchanges[aggregator.superior.name])
                else:
                    self._catalog.set(f"{aggregator.name}.DRL_Strategy.direct_energy_exchanges", direct_exchanges[aggregator.superior.name])

        # Publishing the needs
        if aggregator.contract:

            quantities_and_prices.append(message)
            quantities_and_prices = self._publish_needs(aggregator, quantities_and_prices)

        # Counter to call ascending and descending interfaces with my code
        if self.counter == len(self.scope) + 1:
            self.counter = 1
        else:
            self.counter += 1

        return quantities_and_prices

    def top_down_phase(self, aggregator):
        # TODO voir comment traiter les conversions
        # TODO confirmer la proposition de decision message avec Timothé
        # TODO valider avec Timothé la manière de calculer les energy bought/sold inside/outside et money earned/spent inside/outside

        energy_bought_outside = 0.0
        money_spent_outside = 0.0
        energy_sold_outside = 0.0
        money_earned_outside = 0.0
        maximum_energy_consumed = self._catalog.get(f"{aggregator.name}.maximum_energy_consumption")
        maximum_energy_produced = self._catalog.get(f"{aggregator.name}.maximum_energy_production")

        # Ensuring communication with the RL agent
        if self.counter % len(self.scope) == 0:
            updating_grid_state(self._catalog, self.agent)  # communicating the information to the RL agent
            getting_agent_decision(self._catalog, self.agent)  # retrieving the decision taken by the RL agent
            self.counter += 1

        # we retrieve the energy accorded to each aggregator with the decision taken by the RL agent
        [energy_accorded_to_consumers, energy_accorded_to_producers, energy_accorded_to_storage] = extract_decision(self._catalog.get("DRL_Strategy.decision_message"), aggregator)
        energy_accorded_to_exchange = retrieve_concerned_energy_exchanges(self._catalog.get(f"DRL_Strategy.exchanges_message"), aggregator)
        buying_price, selling_price = self._catalog.get(f"{aggregator.name}.DRL_Strategy.energy_prices").values()

        # Energy distribution and billing
        # First we have to get the list of devices according to their use
        device_list = []
        consumers_list = []
        producers_list = []
        storage_list = []
        converters_list = {}
        message = {**self.messages_manager.create_decision_message()}
        # Getting the list of all the devices directly managed by the aggregator
        for device_name in aggregator.devices:
            device_list.append(self._catalog.devices[device_name])

        for device in device_list:
            specific_message = device.messages_manager.get_information_message
            if specific_message["type"] == "standard":
                Emax = self._catalog.get(f"{device.name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]
                if Emax > 0:  # the energy system consumes energy
                    consumers_list.append(device)  # the list of energy consumption systems
                elif Emax < 0:  # the energy system produces energy
                    producers_list.append(device)  # the list of energy production systems
            elif specific_message["type"] == "storage":  # the list of energy storage systems
                storage_list.append(device)
            elif specific_message["type"] == "converter":  # the list of energy conversion systems
                converters_list[device.name] = device.device_aggregators

        # Energy conversion and exchanges
        if not self.agent.inference_flag:  # if we are training the model
            grid_topology = self.agent.grid.get_topology
        else:
            grid_topology = self.agent.grid_topology
        bought_inside, spent_inside, sold_inside, earned_inside, bought_outside, spent_outside, sold_outside, earned_outside = distribute_energy_exchanges(self._catalog, aggregator, energy_accorded_to_exchange, grid_topology, converters_list, buying_price, selling_price, message, self.scope)

        # The energy is then distributed to the devices directly managed by the aggregator
        # Energy consumption
        energy_sold_inside, money_earned_inside = distribute_to_standard_devices(consumers_list, energy_accorded_to_consumers, buying_price, self._catalog, aggregator, message)

        # Energy production
        energy_bought_inside, money_spent_inside = distribute_to_standard_devices(producers_list, energy_accorded_to_producers, selling_price, self._catalog, aggregator, message)

        # Energy storage
        energy_bought, money_spent, energy_sold, money_earned = distribute_to_storage_devices(storage_list, energy_accorded_to_storage, buying_price, selling_price, self._catalog, aggregator, message)

        # Energy & prices balance of the aggregator - Managed inside (only devices directly managed by the aggregator)
        energy_bought_inside += energy_bought
        money_spent_inside += money_spent
        energy_sold_inside += energy_sold
        money_earned_inside += money_earned


        # Energy & prices balance of the aggregator - Energy exchange with outside (direct ones and with conversion)
        energy_bought_inside += bought_inside
        money_spent_inside += spent_inside
        energy_sold_inside += sold_inside
        money_earned_inside += earned_inside

        energy_bought_outside += bought_outside
        money_spent_outside += spent_outside
        energy_sold_outside += sold_outside
        money_earned_outside += earned_outside

        self._update_balances(aggregator, energy_bought_inside, energy_bought_outside, energy_sold_inside, energy_sold_outside, money_spent_inside, money_spent_outside, money_earned_inside, money_earned_outside, maximum_energy_consumed, maximum_energy_produced)

    def multi_energy_balance_check(self, aggregator):  # todo verifier avec Timothé que ça ne pose pas de problème
        pass

