# This file, we create a strategy sub-class that will be used for the Deep Reinforcement Learning method.
# It updates the balance of each aggregator with the action/decision taken by the RL agent.
# The decision is taken at each iteration and it is translated with the strategy_interface.

# Imports
from src.common.Strategy import Strategy
from interface_peacefulness import *


class DeepReinforcementLearning(Strategy):

    def __init__(self, agent: "A3C_agent"):
        super().__init__("deep_reinforcement_learning_strategy", "The optimal energy management strategy that will be learned by the RL agent")
        self.agent = agent
        self.counter = 0  # will be used to send and receive information from the RL agent
        self.scope = None  # list of aggregators managed by this strategy in particular for Multi-Agent purposes

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
        message = aggregator.information_message()

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
        formalism_message, converter_message = my_devices(self._catalog, aggregator)
        formalism_message = mutualize_formalism_message(formalism_message)  # TODO sous l'hypothèse de prendre les valeurs moyennes & ratios pour flex/inter

        # Data on rigid energy consumption and production forecasting
        forecasting_message = self.call_to_forecast(aggregator)  # this dict is to be sent to the RL agent
        if forecasting_message is not None:
            if f"{aggregator.name}.DRL_Strategy.forecasting_message" not in self._catalog.keys:
                self._catalog.add(f"{aggregator.name}.DRL_Strategy.forecasting_message", forecasting_message)
            else:
                self._catalog.set(f"{aggregator.name}.DRL_Strategy.forecasting_message", forecasting_message)

        # Correction of the considered quantities
        # todo (verification with the self.limit_quantities doesn't work because the storage is only considered when its Emin and Emax have different signs)
        minimum_energy_consumed = 0  # the minimum quantity of energy needed to be consumed
        minimum_energy_produced = 0  # the minimum quantity of energy needed to be produced
        maximum_energy_consumed = 0  # the maximum quantity of energy needed to be consumed
        maximum_energy_produced = 0  # the maximum quantity of energy needed to be produced
        maximum_energy_charge = 0  # the maximum quantity of energy acceptable by storage charge
        maximum_energy_discharge = 0  # the maximum quantity of energy available from storage discharge
        [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, maximum_energy_charge, maximum_energy_discharge] = self._limit_quantities(aggregator, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, maximum_energy_charge, maximum_energy_discharge)
        if f"{aggregator.name}.DRL_Strategy.direct_energy_maximum_quantities" not in self._catalog.keys:
            self._catalog.add(f"{aggregator.name}.DRL_Strategy.direct_energy_maximum_quantities", {"consumption": maximum_energy_consumed, "production": maximum_energy_produced})
        else:
            self._catalog.set(f"{aggregator.name}.DRL_Strategy.direct_energy_maximum_quantities", {"consumption": maximum_energy_consumed, "production": maximum_energy_produced})
        # Storage energy systems are only considered if they provide flexibility
        if maximum_energy_charge == 0 and maximum_energy_discharge == 0:
            formalism_message['Energy_Consumption']["energy_minimum"] = minimum_energy_consumed
            formalism_message['Energy_Consumption']["energy_maximum"] = maximum_energy_consumed
            formalism_message['Energy_Production']["energy_minimum"] = - minimum_energy_produced
            formalism_message['Energy_Production']["energy_maximum"] = - maximum_energy_produced
            formalism_message['Energy_Storage']["energy_minimum"] = 0
            formalism_message['Energy_Storage']["energy_maximum"] = 0

        if f"{aggregator.name}.DRL_Strategy.formalism_message" not in self._catalog.keys:
            self._catalog.add(f"{aggregator.name}.DRL_Strategy.formalism_message", formalism_message)
        else:
            self._catalog.set(f"{aggregator.name}.DRL_Strategy.formalism_message", formalism_message)
        if f"{aggregator.name}.DRL_Strategy.converter_message" not in self._catalog.keys:
            self._catalog.add(f"{aggregator.name}.DRL_Strategy.converter_message", converter_message[aggregator.name])
        else:
            self._catalog.set(f"{aggregator.name}.DRL_Strategy.converter_message", converter_message[aggregator.name])

        # We define the min/max energy produced/consumed
        message["energy_minimum"] = - aggregator.capacity["selling"]
        message["energy_nominal"] = 0.0
        message["energy_maximum"] = aggregator.capacity["buying"]
        # Publishing the needs (before sending direct energy exchanges data to the RL agent to take the contract into account)
        if aggregator.contract:
            quantities_and_prices.append(message)
            quantities_and_prices = self._publish_needs(aggregator, quantities_and_prices)

        # The aggregator publishes its need to the aggregator superior
        if aggregator.superior:  # todo voir comment se passer de cette limite
            if aggregator.nature.name == aggregator.superior.nature.name:
                if len(quantities_and_prices) == 1:
                    if f"Energy asked from {aggregator.name} to {aggregator.superior.name}" not in self._catalog.keys:
                        self._catalog.add(f"Energy asked from {aggregator.name} to {aggregator.superior.name}", quantities_and_prices[0])
                    else:
                        self._catalog.set(f"Energy asked from {aggregator.name} to {aggregator.superior.name}", quantities_and_prices[0])
                else:
                    raise Exception("The current version of the code doesn't handle more than proposal/message from and aggregator to its superior !")

        # Data related to the hierarchical energy exchanges (between subaggregators and superior)
        direct_exchanges = {}
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

        # Counter to call ascending and descending interfaces with my code
        if self.counter == len(self.scope) + 1:
            self.counter = 1
        else:
            self.counter += 1

        return quantities_and_prices

    def top_down_phase(self, aggregator):
        # todo nouvelle version à checker la logique de la résolution avec Timothé
        # Ensuring communication with the RL agent
        if self.counter % len(self.scope) == 0:
            updating_grid_state(self._catalog, self.agent)  # communicating the information to the RL agent
            getting_agent_decision(self._catalog, self.agent)  # retrieving the decision taken by the RL agent
            self.counter += 1

        # Initialization
        energy_bought_outside = 0  # the absolute value of energy bought outside
        energy_sold_outside = 0  # the absolute value of energy sold outside
        energy_bought_inside = 0  # the absolute value of energy bought inside
        energy_sold_inside = 0  # the absolute value of energy sold inside

        money_earned_outside = 0  # the absolute value of money earned outside
        money_spent_outside = 0  # the absolute value of money spent outside
        money_earned_inside = 0  # the absolute value of money earned inside
        money_spent_inside = 0  # the absolute value of money spent inside

        # Retrieving the energy accorded to each aggregator with the decision taken by the RL agent
        [energy_accorded_to_consumers, energy_accorded_to_producers, energy_accorded_to_storage] = extract_decision(self._catalog.get("DRL_Strategy.decision_message"), aggregator)
        energy_accorded_to_exchange = retrieve_concerned_energy_exchanges(self._catalog.get(f"DRL_Strategy.exchanges_message"), aggregator)
        internal_buying_price, internal_selling_price = self._catalog.get(f"{aggregator.name}.DRL_Strategy.energy_prices").values()
        maximum_energy_consumed, maximum_energy_produced = self._catalog.get(f"{aggregator.name}.DRL_Strategy.direct_energy_maximum_quantities").values()

        # Checking first the superior message todo patchwork solution working for only the case where the superior is the main grid and has infinite exchange capacity
        if aggregator.superior not in self.scope:  # todo we should check if the message is a list of dicts (multiple messages) or just one dict
            old_energy_accorded_from_superior = self._catalog.get(f"{aggregator.name}.{aggregator.superior.nature.name}.energy_accorded")
            # todo est-ce qu'on le laisse decider le prix ?
            if not isinstance(old_energy_accorded_from_superior, list):
                for tup in energy_accorded_to_exchange.keys():
                    if aggregator.superior.name in tup:
                        old_energy_accorded_from_superior["quantity"] = - energy_accorded_to_exchange[tup]
                        self._catalog.set(f"{aggregator.name}.{aggregator.superior.nature.name}.energy_accorded", old_energy_accorded_from_superior)
            else:  # todo or we should just do a loop over all the elements instead
                for tup in energy_accorded_to_exchange.keys():
                    if aggregator.superior.name in tup:
                        old_energy_accorded_from_superior[0]["quantity"] = - energy_accorded_to_exchange[tup]  # todo patchwork solution ? (what about other outside energy exchanges ?)
                        self._catalog.set(f"{aggregator.name}.{aggregator.superior.nature.name}.energy_accorded", old_energy_accorded_from_superior)
        # balance of the exchanges made with outside (todo check the signs + what about conversion systems ?)
        [money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside] = self._exchanges_balance(aggregator, money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside)

        # Internal balance
        [sorted_demands, sorted_offers, sorted_storage] = self._separe_quantities(aggregator)  # sorting the quantities

        # determination of storage usage
        if energy_accorded_to_storage < 0:  # if the energy storage systems are discharging
            for message in sorted_storage:
                self._transform_storage_into_production(message)
            [energy_accorded_to_storage, money_spent_inside, energy_bought_inside] = self._distribute_production_full_service(aggregator, internal_selling_price, sorted_storage, - energy_accorded_to_storage, money_spent_inside, energy_bought_inside)

        else:  # if they are charging
            for message in sorted_storage:
                self._transform_storage_into_consumption(message)
            [energy_accorded_to_storage, money_earned_inside, energy_sold_inside] = self._distribute_consumption_full_service(aggregator, internal_buying_price, sorted_storage, energy_accorded_to_storage, money_earned_inside, energy_sold_inside)

        # distribution is then decided for the managed devices and subaggregators which are urgent
        [sorted_demands, energy_accorded_to_consumers, money_earned_inside, energy_sold_inside] = self._serve_emergency_demands(aggregator, internal_buying_price, sorted_demands, energy_accorded_to_consumers, money_earned_inside, energy_sold_inside)
        [sorted_offers, energy_accorded_to_producers, money_spent_inside, energy_bought_inside] = self._serve_emergency_offers(aggregator, internal_selling_price, sorted_offers, - energy_accorded_to_producers, money_spent_inside, energy_bought_inside)

        # then the remaining quantities for the non-urgent ones is equally distributed
        [energy_accorded_to_consumers, money_earned_inside, energy_sold_inside] = self._distribute_consumption_partial_service(aggregator, internal_buying_price, sorted_demands, energy_accorded_to_consumers, money_earned_inside, energy_sold_inside)
        [energy_accorded_to_producers, money_spent_inside, energy_bought_inside] = self._distribute_production_partial_service(aggregator, internal_selling_price, sorted_offers, energy_accorded_to_producers, money_spent_inside, energy_bought_inside)

        self._update_balances(aggregator, energy_bought_inside, energy_bought_outside, energy_sold_inside, energy_sold_outside, money_spent_inside, money_spent_outside, money_earned_inside, money_earned_outside, maximum_energy_consumed, maximum_energy_produced)


        # TODO voir comment traiter les conversions
        # TODO confirmer la proposition de decision message avec Timothé
        # TODO valider avec Timothé la manière de calculer les energy bought/sold inside/outside et money earned/spent inside/outside

    def multi_energy_balance_check(self, aggregator):  # todo verifier avec Timothé que ça ne pose pas de problème
        pass

