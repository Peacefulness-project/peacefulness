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
        # print(f"i am the scope : {self.scope}")
        quantities_and_prices = []
        # message = {**self._create_information_message()}
        message = aggregator.information_message()
        # print(f"\ni am the message created from self.create_information_message : {message}")

        # Data on energy prices
        [min_price, max_price] = self._limit_prices(aggregator)  # thresholds of accepted energy prices
        # print(f"\ni am the min price (selling) from self.limit_prices : {min_price}")
        # print(f"\ni am the max price (buying) from self.limit_prices : {max_price}")
        # these two values are to be sent to the RL agent (part of the MEG state)
        buying_price, selling_price = determine_energy_prices(self._catalog, aggregator, min_price, max_price)
        # print(f"\ni am the internal buying price from determine_energy_prices : {buying_price}")
        # print(f"\ni am the internal selling price from determine_energy_prices : {selling_price}")
        if f"{aggregator.name}.DRL_Strategy.energy_prices" not in self._catalog.keys:
            self._catalog.add(f"{aggregator.name}.DRL_Strategy.energy_prices", {"buying_price": buying_price, "selling_price": selling_price})
        else:
            self._catalog.set(f"{aggregator.name}.DRL_Strategy.energy_prices", {"buying_price": buying_price, "selling_price": selling_price})

        message["price"] = (buying_price + selling_price) / 2  # this value is the one published in the catalog
        # print(f"\ni am the price that message stores with the price my superior aggregator sees : {message}")

        # Data related to the formalism variables and lateral energy exchanges (with energy conversion systems)
        formalism_message, converter_message = my_devices(self._catalog, aggregator)
        # print(f"\ni am the information message of each system : {formalism_message}")
        # print(f"\ni am the information message of conversion systems : {converter_message}")
        formalism_message = mutualize_formalism_message(formalism_message)  # TODO sous l'hypothèse de prendre les valeurs moyennes & ratios pour flex/inter
        # print(f"\ni am the mutualized formalism message for each aggregator : {formalism_message}")

        # Data on rigid energy consumption and production forecasting
        forecasting_message = self.call_to_forecast(aggregator)  # this dict is to be sent to the RL agent
        # print(f"\ni am the forecasting message for each aggregator : {forecasting_message}")
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
        # todo these two values can be the floating bounds to my reward function if penalizing with Timothé's idea about having just three actions
        # min_exchange_energy = - (minimum_energy_consumed + maximum_energy_charge - minimum_energy_produced)  # todo à confirmer
        # max_exchange_energy = - (maximum_energy_consumed - maximum_energy_discharge - maximum_energy_produced) # todo à confirmer
        # print(f"\ni am the maximum amount of energy to be consumed for the aggregator {aggregator.name}: {maximum_energy_consumed}")
        # print(f"\ni am the maximum amount of energy to be produced for the aggregator {aggregator.name}: {maximum_energy_produced}")
        # print(f"\ni am the minimum amount of energy to be consumed for the aggregator {aggregator.name}: {minimum_energy_consumed}")
        # print(f"\ni am the minimum amount of energy to be produced for the aggregator {aggregator.name}: {minimum_energy_produced}")
        # print(f"\ni am the maximum amount of energy to be charged for the aggregator {aggregator.name}: {maximum_energy_charge}")
        # print(f"\ni am the maximum amount of energy to be discharged for the aggregator {aggregator.name}: {maximum_energy_discharge}")
        if f"{aggregator.name}.DRL_Strategy.direct_energy_maximum_quantities" not in self._catalog.keys:
            self._catalog.add(f"{aggregator.name}.DRL_Strategy.direct_energy_maximum_quantities", {"consumption": maximum_energy_consumed, "production": maximum_energy_produced})
        else:
            self._catalog.set(f"{aggregator.name}.DRL_Strategy.direct_energy_maximum_quantities", {"consumption": maximum_energy_consumed, "production": maximum_energy_produced})
        # Storage energy systems are only considered if they provide flexibility
        if maximum_energy_charge == 0 and maximum_energy_discharge == 0:
            # print(f"I am the energy storage formalism message if storage doesn't provide flexibility: {formalism_message['Energy_Storage']}")
            # for my_key in formalism_message['Energy_Storage'].keys():
            #     formalism_message['Energy_Storage'][my_key] = 0
                # print(f"I am the energy storage formalism message if storage doesn't provide flexibility after modification: {formalism_message['Energy_Storage']}")
            formalism_message['Energy_Consumption']["energy_minimum"] = minimum_energy_consumed
            formalism_message['Energy_Consumption']["energy_maximum"] = maximum_energy_consumed
            formalism_message['Energy_Production']["energy_minimum"] = - minimum_energy_produced
            formalism_message['Energy_Production']["energy_maximum"] = - maximum_energy_produced
            formalism_message['Energy_Storage']["energy_minimum"] = 0
            formalism_message['Energy_Storage']["energy_maximum"] = 0
            # print(f"\ni am the formalism message corrected by self._limit_quantities: {formalism_message}")

        if f"{aggregator.name}.DRL_Strategy.formalism_message" not in self._catalog.keys:
            self._catalog.add(f"{aggregator.name}.DRL_Strategy.formalism_message", formalism_message)
        else:
            self._catalog.set(f"{aggregator.name}.DRL_Strategy.formalism_message", formalism_message)
        if f"{aggregator.name}.DRL_Strategy.converter_message" not in self._catalog.keys:
            self._catalog.add(f"{aggregator.name}.DRL_Strategy.converter_message", converter_message[aggregator.name])
        else:
            self._catalog.set(f"{aggregator.name}.DRL_Strategy.converter_message", converter_message[aggregator.name])

        # if abs(minimum_energy_consumed) != abs(formalism_message['Energy_Consumption']["energy_minimum"]):
        #     raise Exception('Grouping the systems typologies does not yield correct results ; hint -> min_consumption')
        # if abs(maximum_energy_consumed) != abs(formalism_message['Energy_Consumption']["energy_maximum"]):
        #     raise Exception('Grouping the systems typologies does not yield correct results ; hint -> max_consumption')
        # if abs(minimum_energy_produced) != abs(formalism_message['Energy_Production']["energy_minimum"]):
        #     raise Exception('Grouping the systems typologies does not yield correct results ; hint -> min_production')
        # if abs(maximum_energy_produced) != abs(formalism_message['Energy_Production']["energy_maximum"]):
        #     raise Exception('Grouping the systems typologies does not yield correct results ; hint -> max_production')
        # if abs(maximum_energy_charge) != abs(formalism_message['Energy_Storage']["energy_maximum"]):
        #     raise Exception('Grouping the systems typologies does not yield correct results ; hint -> max_storage')
        # if abs(maximum_energy_discharge) != abs(formalism_message['Energy_Storage']["energy_minimum"]):
        #     raise Exception('Grouping the systems typologies does not yield correct results ; hint -> min_storage')
        # print(f"i am the min energy to be consumed : {minimum_energy_consumed}")
        # print(f"i am the max energy to be consumed : {maximum_energy_consumed}")
        # print(f"i am the min energy to be produced : {minimum_energy_produced}")
        # print(f"i am the max energy to be produced : {maximum_energy_produced}")
        # print(f"i am the energy to be charged : {maximum_energy_charge}")
        # print(f"i am the energy to be discharged : {maximum_energy_discharge}")
        # storable = self._catalog.get(f"{aggregator.name}.energy_storable")
        # stored = self._catalog.get(f"{aggregator.name}.energy_stored")
        # print(f"i am the energy stored: {stored}")
        # print(f"i am the energy storable : {storable}")
        # # The aggregator publishes its needs
        # energy_difference = maximum_energy_consumed - maximum_energy_produced
        # message["energy_minimum"] = energy_difference
        # message["energy_nominal"] = energy_difference
        # message["energy_maximum"] = energy_difference

        # TODO verify this proposal with Timothé
        # We define the min/max energy produced/consumed (todo - voir si ça marche)
        message["energy_minimum"] = - aggregator.capacity["selling"]
        message["energy_nominal"] = 0.0
        message["energy_maximum"] = aggregator.capacity["buying"]
        # Publishing the needs (before sending direct energy exchanges data to the RL agent to take the contract into account)
        if aggregator.contract:
            quantities_and_prices.append(message)
            # print(f"\n I am the quantities_and_prices message before contract modification : {quantities_and_prices}")
            quantities_and_prices = self._publish_needs(aggregator, quantities_and_prices)
            # print(f"\n I am the quantities_and_prices message after contract modification : {quantities_and_prices}")

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
                # message["energy_minimum"] = message["energy_minimum"] * aggregator.efficiency
                # message["energy_nominal"] = message["energy_nominal"] * aggregator.efficiency
                # message["energy_maximum"] = message["energy_maximum"] * aggregator.efficiency
                # print(f"\ni am the message sent to my aggregator superior regarding my needs : {message}")

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
            # print(f"\ni am the direct energy exchanges message : {direct_exchanges}")
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
        # print(f"the energy accorded to consumers inside the top_down_phase with extract_decision method: {energy_accorded_to_consumers}")
        # print(f"the energy accorded to producers inside the top_down_phase with extract_decision method: {energy_accorded_to_producers}")
        # print(f"the energy accorded to storage inside the top_down_phase with extract_decision method: {energy_accorded_to_storage}")
        # print(f"the energy accorded to exchange inside the top_down_phase with retrieve_concerned_energy_exchanges method: {energy_accorded_to_exchange}")
        # Checking first the superior message todo patchwork solution working for only the case where the superior is the main grid and has infinite exchange capacity
        if aggregator.superior not in self.scope:  # todo we should check if the message is a list of dicts (multiple messages) or just one dict
            old_energy_accorded_from_superior = self._catalog.get(f"{aggregator.name}.{aggregator.superior.nature.name}.energy_accorded")
            # print(f"i am the old energy_accorded message before modification (decided by the grid) : {old_energy_accorded_from_superior}")
            # todo est-ce qu'on le laisse decider le prix ?
            # energy_asked_from_superior = self._catalog.get(f"Energy asked from {aggregator.name} to {aggregator.superior.name}")
            if not isinstance(old_energy_accorded_from_superior, list):
                for tup in energy_accorded_to_exchange.keys():
                    if aggregator.superior.name in tup:
                        old_energy_accorded_from_superior["quantity"] = - energy_accorded_to_exchange[tup]
                        # old_energy_accorded_from_superior["price"] = energy_asked_from_superior["price"]
                        # print(f"i am the old energy_accorded message after modification (decided by the DRL_Strategy) : {old_energy_accorded_from_superior}")
                        self._catalog.set(f"{aggregator.name}.{aggregator.superior.nature.name}.energy_accorded", old_energy_accorded_from_superior)
            else:  # todo or we should just do a loop over all the elements instead
                for tup in energy_accorded_to_exchange.keys():
                    if aggregator.superior.name in tup:
                        old_energy_accorded_from_superior[0]["quantity"] = - energy_accorded_to_exchange[tup]  # todo patchwork solution ? (what about other outside energy exchanges ?)
                        # old_energy_accorded_from_superior["price"] = energy_asked_from_superior["price"]
                        # print(f"i am the old energy_accorded message (as a list) after modification (decided by the DRL_Strategy) : {old_energy_accorded_from_superior}")
                        self._catalog.set(f"{aggregator.name}.{aggregator.superior.nature.name}.energy_accorded", old_energy_accorded_from_superior)
        # balance of the exchanges made with outside (todo check the signs + what about conversion systems ?)
        [money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside] = self._exchanges_balance(aggregator, money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside)
        # print(f"\nThe money spent outside (calculated with self._exchanges_balance) : {money_spent_outside}")
        # print(f"\nThe energy bought outside (calculated with self._exchanges_balance) : {energy_bought_outside}")
        # print(f"\nThe money earned outside (calculated with self._exchanges_balance) : {money_earned_outside}")
        # print(f"\nThe energy sold outside (calculated with self._exchanges_balance) : {energy_sold_outside}")
        # Internal balance
        [sorted_demands, sorted_offers, sorted_storage] = self._separe_quantities(aggregator)  # sorting the quantities
        # print(f"\ni am the energy demands: {sorted_demands}")
        # print(f"\ni am the energy offers: {sorted_offers}")
        # print(f"\ni am the sorted storage: {sorted_storage}")
        # determination of available energy # todo à checker
        # energy_available_production = energy_accorded_to_producers + energy_bought_outside
        # energy_available_consumption = energy_accorded_to_consumers + energy_sold_outside
        # determination of storage usage
        if energy_accorded_to_storage < 0:  # if the energy storage systems are discharging
            for message in sorted_storage:
                # print(f"\ni am storage message when the battery wants to discharge (before transformation into producer) : {message}")
                self._transform_storage_into_production(message)
                # print(f"\ni am storage message when the battery wants to discharge (after transformation into producer) : {message}")
            # print(f"\ni am the storage energy accorded to discharge (production) before distribution: {energy_accorded_to_storage}")
            [energy_accorded_to_storage, money_spent_inside, energy_bought_inside] = self._distribute_production_full_service(aggregator, internal_selling_price, sorted_storage, - energy_accorded_to_storage, money_spent_inside, energy_bought_inside)
            # print(f"\ni am the storage energy accorded to discharge (production) after storage distribution: {energy_accorded_to_storage}")
            # print(f"\ni am the money spent inside after storage distribution to production: {money_spent_inside}")
            # print(f"\ni am the energy bought inside after storage distribution to production: {energy_bought_inside}")
        else:  # if they are charging
            for message in sorted_storage:
                # print(f"\ni am storage message when the battery wants to charge (before transformation into consumer) : {message}")
                self._transform_storage_into_consumption(message)
                # print(f"\ni am storage message when the battery wants to charge (after transformation into consumer) : {message}")
            # print(f"\ni am the storage energy accorded to charge (consumption) before distribution: {energy_accorded_to_storage}")
            [energy_accorded_to_storage, money_earned_inside, energy_sold_inside] = self._distribute_consumption_full_service(aggregator, internal_buying_price, sorted_storage, energy_accorded_to_storage, money_earned_inside, energy_sold_inside)
            # print(f"\ni am the storage energy accorded to charge (consumption) after storage distribution: {energy_accorded_to_storage}")
            # print(f"\ni am the money earned inside after storage distribution to consumption: {money_earned_inside}")
            # print(f"\ni am the energy sold inside after storage distribution to consumption: {energy_sold_inside}")
        # distribution is then decided for the managed devices and subaggregators which are urgent
        # print(f"\n before serving emergency demands, here is the energy accorded to consumers: {energy_accorded_to_consumers}")
        [sorted_demands, energy_accorded_to_consumers, money_earned_inside, energy_sold_inside] = self._serve_emergency_demands(aggregator, internal_buying_price, sorted_demands, energy_accorded_to_consumers, money_earned_inside, energy_sold_inside)
        # print(f"\n after serving emergency demands, here is the energy accorded to consumers (left): {energy_accorded_to_consumers}")
        # print(f"\n after serving emergency demands, here is the money earned inside: {money_earned_inside}")
        # print(f"\n after serving emergency demands, here is the energy sold inside: {energy_sold_inside}")
        # print(f"\n after serving emergency demands, here is the sorted_demands left: {sorted_demands}")
        # print(f"\n before serving emergency offers, here is the energy accorded to producers: {energy_accorded_to_producers}")
        [sorted_offers, energy_accorded_to_producers, money_spent_inside, energy_bought_inside] = self._serve_emergency_offers(aggregator, internal_selling_price, sorted_offers, - energy_accorded_to_producers, money_spent_inside, energy_bought_inside)
        # print(f"\n after serving emergency offers, here is the energy accorded to producers (left): {energy_accorded_to_producers}")
        # print(f"\n after serving emergency offers, here is the money spent inside: {money_spent_inside}")
        # print(f"\n after serving emergency offers, here is the energy bought inside: {energy_bought_inside}")
        # print(f"\n after serving emergency offers, here is the sorted_offers left: {sorted_offers}")
        # then the remaining quantities for the non-urgent ones is equally distributed
        [energy_accorded_to_consumers, money_earned_inside, energy_sold_inside] = self._distribute_consumption_partial_service(aggregator, internal_buying_price, sorted_demands, energy_accorded_to_consumers, money_earned_inside, energy_sold_inside)
        # print(f"\n after serving the demands left (non-urgent), here is the energy accorded to consumers left : {energy_accorded_to_consumers}")
        # print(f"\n after serving the demands left (non-urgent), here is the money earned inside : {money_earned_inside}")
        # print(f"\n after serving the demands left (non-urgent), here is the energy sold inside : {energy_sold_inside}")
        [energy_accorded_to_producers, money_spent_inside, energy_bought_inside] = self._distribute_production_partial_service(aggregator, internal_selling_price, sorted_offers, energy_accorded_to_producers, money_spent_inside, energy_bought_inside)
        # print(f"\n after serving the offers left (non-urgent), here is the energy accorded to producers left : {energy_accorded_to_producers}")
        # print(f"\n after serving the offers left (non-urgent), here is the money spent inside : {money_spent_inside}")
        # print(f"\n after serving the offers left (non-urgent), here is the energy bought inside : {energy_bought_inside}")

        self._update_balances(aggregator, energy_bought_inside, energy_bought_outside, energy_sold_inside, energy_sold_outside, money_spent_inside, money_spent_outside, money_earned_inside, money_earned_outside, maximum_energy_consumed, maximum_energy_produced)


        # TODO voir comment traiter les conversions
        # TODO confirmer la proposition de decision message avec Timothé
        # TODO valider avec Timothé la manière de calculer les energy bought/sold inside/outside et money earned/spent inside/outside

        # energy_bought_outside = 0.0
        # money_spent_outside = 0.0
        # energy_sold_outside = 0.0
        # money_earned_outside = 0.0
        # maximum_energy_consumed = self._catalog.get(f"{aggregator.name}.maximum_energy_consumption")
        # maximum_energy_produced = self._catalog.get(f"{aggregator.name}.maximum_energy_production")
        #
        # # Ensuring communication with the RL agent
        # if self.counter % len(self.scope) == 0:
        #     updating_grid_state(self._catalog, self.agent)  # communicating the information to the RL agent
        #     getting_agent_decision(self._catalog, self.agent)  # retrieving the decision taken by the RL agent
        #     self.counter += 1
        #
        # # we retrieve the energy accorded to each aggregator with the decision taken by the RL agent
        # [energy_accorded_to_consumers, energy_accorded_to_producers, energy_accorded_to_storage] = extract_decision(self._catalog.get("DRL_Strategy.decision_message"), aggregator)
        # energy_accorded_to_exchange = retrieve_concerned_energy_exchanges(self._catalog.get(f"DRL_Strategy.exchanges_message"), aggregator)
        # buying_price, selling_price = self._catalog.get(f"{aggregator.name}.DRL_Strategy.energy_prices").values()
        #
        # # Energy distribution and billing
        # # First we have to get the list of devices according to their use
        # device_list = []
        # consumers_list = []
        # producers_list = []
        # storage_list = []
        # converters_list = {}
        # message = {**self.messages_manager.create_decision_message()}
        # # Getting the list of all the devices directly managed by the aggregator
        # for device_name in aggregator.devices:
        #     device_list.append(self._catalog.devices[device_name])
        #
        # for device in device_list:
        #     specific_message = device.messages_manager.get_information_message
        #     if specific_message["type"] == "standard":
        #         Emax = self._catalog.get(f"{device.name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]
        #         if Emax > 0:  # the energy system consumes energy
        #             consumers_list.append(device)  # the list of energy consumption systems
        #         elif Emax < 0:  # the energy system produces energy
        #             producers_list.append(device)  # the list of energy production systems
        #     elif specific_message["type"] == "storage":  # the list of energy storage systems
        #         storage_list.append(device)
        #     elif specific_message["type"] == "converter":  # the list of energy conversion systems
        #         converters_list[device.name] = device.device_aggregators
        #
        # # Energy conversion and exchanges
        # if not self.agent.inference_flag:  # if we are training the model
        #     grid_topology = self.agent.grid.get_topology
        # else:  # if we are using a trained model
        #     grid_topology = self.agent.grid_topology
        # bought_inside, spent_inside, sold_inside, earned_inside, bought_outside, spent_outside, sold_outside, earned_outside = distribute_energy_exchanges(self._catalog, aggregator, energy_accorded_to_exchange, grid_topology, converters_list, buying_price, selling_price, message, self.scope)
        #
        # # The energy is then distributed to the devices directly managed by the aggregator
        # # Energy consumption
        # energy_sold_inside, money_earned_inside = distribute_to_standard_devices(consumers_list, energy_accorded_to_consumers, buying_price, self._catalog, aggregator, message)
        #
        # # Energy production
        # energy_bought_inside, money_spent_inside = distribute_to_standard_devices(producers_list, energy_accorded_to_producers, selling_price, self._catalog, aggregator, message)
        #
        # # Energy storage
        # energy_bought, money_spent, energy_sold, money_earned = distribute_to_storage_devices(storage_list, energy_accorded_to_storage, buying_price, selling_price, self._catalog, aggregator, message)
        #
        # # Energy & prices balance of the aggregator - Managed inside (only devices directly managed by the aggregator)
        # energy_bought_inside += energy_bought
        # money_spent_inside += money_spent
        # energy_sold_inside += energy_sold
        # money_earned_inside += money_earned
        #
        #
        # # Energy & prices balance of the aggregator - Energy exchange with outside (direct ones and with conversion)
        # energy_bought_inside += bought_inside
        # money_spent_inside += spent_inside
        # energy_sold_inside += sold_inside
        # money_earned_inside += earned_inside
        #
        # energy_bought_outside += bought_outside
        # money_spent_outside += spent_outside
        # energy_sold_outside += sold_outside
        # money_earned_outside += earned_outside
        #
        # self._update_balances(aggregator, energy_bought_inside, energy_bought_outside, energy_sold_inside, energy_sold_outside, money_spent_inside, money_spent_outside, money_earned_inside, money_earned_outside, maximum_energy_consumed, maximum_energy_produced)

    def multi_energy_balance_check(self, aggregator):  # todo verifier avec Timothé que ça ne pose pas de problème
        pass

