# Imports
from src.common.Strategy import Strategy
from lib.Subclasses.Strategy.DRLStrategy.DRL_Strategy_utilities import *
from lib.Subclasses.Strategy.SingleAgentDRLStrategy.Utilities import *


class SingleAgentDRLStrategy(Strategy):

    def __init__(self, name=None, optional_params=None):
        strategy_name = name if name is not None else "gym_Strategy"
        super().__init__(strategy_name, "The strategy that will be learned by the RL agent with the Gym environment")

        # To apply the action of the RL agent
        # self._catalog.add(f"{self._name}.decision_message", {})
        # self._catalog.add(f"{self._name}.exchanges_message", {})

        # For hierarchical dispatch with RL decision for the surrogates + GA-based attribution to individual energy systems
        if optional_params:
            self.optimized_distribution_flag = True
            self.sorting_coefficients = optional_params
            if f"{self._name}.sorting_coefficients" not in self._catalog.keys:
                self._catalog.add(f"{self._name}.sorting_coefficients", optional_params)
            else:
                self._catalog.set(f"{self._name}.sorting_coefficients", optional_params)
        else:
            self.optimized_distribution_flag = False

    # ##################################################################################################################
    # Dynamic behavior
    ####################################################################################################################

    def bottom_up_phase(self, aggregator: "Aggregator"):
        # Before publishing quantities and prices to the superior aggregator, we gather relevant information to send to the RL agent
        # Namely, the data needed : energy prices, formalism variables representing the state of the MEG, energy exchanges and forecasting
        quantities_and_prices = []
        message = aggregator.information_message()


        # 1 - Energy prices
        [min_price, max_price] = self._limit_prices(aggregator)  # thresholds of accepted energy prices
        # these two values are to be sent to the RL agent (part of the MEG state)
        buying_price, selling_price = determine_energy_prices(self._catalog, aggregator, min_price, max_price)
        if f"{aggregator.name}.{self._name}.energy_prices" not in self._catalog.keys:
            self._catalog.add(f"{aggregator.name}.{self._name}.energy_prices", {"buying_price": deepcopy(buying_price), "selling_price": deepcopy(selling_price)})
        else:
            self._catalog.set(f"{aggregator.name}.{self._name}.energy_prices", {"buying_price": deepcopy(buying_price), "selling_price": deepcopy(selling_price)})

        message["price"] = (buying_price + selling_price) / 2  # this value is the one published in the catalog


        # 2 - Rigid energy consumption and production forecasting
        forecasting_message = self.call_to_forecast(aggregator)  # this dict is to be sent to the RL agent
        if forecasting_message is not None:
            if f"{aggregator.name}.{self._name}.forecasting_message" not in self._catalog.keys:
                self._catalog.add(f"{aggregator.name}.{self._name}.forecasting_message", deepcopy(forecasting_message))
            else:
                self._catalog.set(f"{aggregator.name}.{self._name}.forecasting_message", deepcopy(forecasting_message))


        # 3 - Formalism variables including energy exchanges with energy conversion systems
        formalism_message, converter_message = my_devices(self._catalog, aggregator)
        if f"{aggregator.name}.{self._name}.converter_message" not in self._catalog.keys:
            self._catalog.add(f"{aggregator.name}.{self._name}.converter_message", deepcopy(converter_message[aggregator.name]))
        else:
            self._catalog.set(f"{aggregator.name}.{self._name}.converter_message", deepcopy(converter_message[aggregator.name]))
        formalism_message = mutualize_formalism_message(formalism_message)

        # Correction of the considered quantities
        minimum_energy_consumed = 0  # the minimum quantity of energy needed to be consumed
        minimum_energy_produced = 0  # the minimum quantity of energy needed to be produced
        maximum_energy_consumed = 0  # the maximum quantity of energy needed to be consumed
        maximum_energy_produced = 0  # the maximum quantity of energy needed to be produced
        maximum_energy_charge = 0  # the maximum quantity of energy acceptable by storage charge
        maximum_energy_discharge = 0  # the maximum quantity of energy available from storage discharge
        [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, maximum_energy_charge, maximum_energy_discharge] = self._limit_quantities(aggregator, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, maximum_energy_charge, maximum_energy_discharge)
        if maximum_energy_charge == 0 and maximum_energy_discharge == 0:
            max_conso = deepcopy(maximum_energy_consumed)
            max_prod = deepcopy(maximum_energy_produced)
            formalism_message['Energy_Consumption']["energy_minimum"] = minimum_energy_consumed
            formalism_message['Energy_Consumption']["energy_maximum"] = maximum_energy_consumed
            formalism_message['Energy_Production']["energy_minimum"] = - minimum_energy_produced
            formalism_message['Energy_Production']["energy_maximum"] = - maximum_energy_produced
            if len(formalism_message['Energy_Storage']) > 0:
                formalism_message['Energy_Storage']["energy_minimum"] = 0.0
                formalism_message['Energy_Storage']["energy_maximum"] = 0.0
        else:
            max_conso = deepcopy(maximum_energy_consumed) + deepcopy(maximum_energy_charge)
            max_prod = deepcopy(maximum_energy_produced) + deepcopy(maximum_energy_discharge)

        if f"{aggregator.name}.{self._name}.energy_maximum_quantities" not in self._catalog.keys:
            self._catalog.add(f"{aggregator.name}.{self._name}.energy_maximum_quantities", {"consumption": max_conso, "production": max_prod})
        else:
            self._catalog.set(f"{aggregator.name}.{self._name}.energy_maximum_quantities", {"consumption": max_conso, "production": max_prod})
        if f"{aggregator.name}.{self._name}.energy_minimum_quantities" not in self._catalog.keys:
            self._catalog.add(f"{aggregator.name}.{self._name}.energy_minimum_quantities", {"consumption": deepcopy(minimum_energy_consumed), "production": deepcopy(minimum_energy_produced)})
        else:
            self._catalog.set(f"{aggregator.name}.{self._name}.energy_minimum_quantities", {"consumption": deepcopy(minimum_energy_consumed), "production": deepcopy(minimum_energy_produced)})

        if f"{aggregator.name}.{self._name}.formalism_message" not in self._catalog.keys:
            self._catalog.add(f"{aggregator.name}.{self._name}.formalism_message", deepcopy(formalism_message))
        else:
            self._catalog.set(f"{aggregator.name}.{self._name}.formalism_message", deepcopy(formalism_message))


        # Publishing the needs
        # We define the min/max energy produced/consumed
        message["energy_minimum"] = aggregator.capacity["selling"]
        message["energy_nominal"] = 0.0
        message["energy_maximum"] = aggregator.capacity["buying"]
        if aggregator.contract: # The aggregator publishes its need to the aggregator superior
            quantities_and_prices.append(message)
            quantities_and_prices = self._publish_needs(aggregator, quantities_and_prices)


        # 4 - Hierarchical energy exchanges (between sub-aggregators and superior)
        # To correct the signs - only for the RL agent
        quantities_and_prices[0]["energy_minimum"] = - aggregator.capacity["buying"]
        quantities_and_prices[0]["energy_maximum"] = aggregator.capacity["selling"]
        if aggregator.superior:
            if aggregator.nature.name == aggregator.superior.nature.name:
                if len(quantities_and_prices) == 1:
                    if f"Energy asked from {aggregator.name} to {aggregator.superior.name}" not in self._catalog.keys:
                        self._catalog.add(f"Energy asked from {aggregator.name} to {aggregator.superior.name}", deepcopy(quantities_and_prices[0]))
                    else:
                        self._catalog.set(f"Energy asked from {aggregator.name} to {aggregator.superior.name}", deepcopy(quantities_and_prices[0]))
                else:
                    raise Exception("The current version of the code doesn't handle more than proposal/message from and aggregator to its superior !")

        direct_exchanges = {}
        for subaggregator in aggregator.subaggregators:
            if subaggregator.nature.name == aggregator.nature.name:
                direct_exchanges = {aggregator.name: {subaggregator.name: {}}}
                if f"Energy asked from {subaggregator.name} to {aggregator.name}" in self._catalog.keys:
                    direct_exchanges[aggregator.name][subaggregator.name] = self._catalog.get(f"Energy asked from {subaggregator.name} to {aggregator.name}")
                else:
                    direct_exchanges[aggregator.name][subaggregator.name] = self._catalog.get(f"{subaggregator.name}.{aggregator.nature.name}.energy_wanted")
                if isinstance(direct_exchanges[aggregator.name][subaggregator.name], list):
                    direct_exchanges[aggregator.name][subaggregator.name] = direct_exchanges[aggregator.name][subaggregator.name][0]
                direct_exchanges[aggregator.name][subaggregator.name]["efficiency"] = subaggregator.efficiency
        if aggregator.superior:
            if aggregator.nature.name == aggregator.superior.nature.name:
                direct_exchanges = {**direct_exchanges, **{aggregator.superior.name: {aggregator.name: {}}}}
                direct_exchanges[aggregator.superior.name][aggregator.name] = self._catalog.get(f"Energy asked from {aggregator.name} to {aggregator.superior.name}")
                direct_exchanges[aggregator.superior.name][aggregator.name]["efficiency"] = aggregator.efficiency

        if direct_exchanges:
            if aggregator.name in direct_exchanges:
                if f"{aggregator.name}.{self._name}.direct_energy_exchanges" not in self._catalog.keys:
                    self._catalog.add(f"{aggregator.name}.{self._name}.direct_energy_exchanges", deepcopy(direct_exchanges[aggregator.name]))
                else:
                    self._catalog.set(f"{aggregator.name}.{self._name}.direct_energy_exchanges", deepcopy(direct_exchanges[aggregator.name]))
            else:
                if f"{aggregator.name}.{self._name}.direct_energy_exchanges" not in self._catalog.keys:
                    self._catalog.add(f"{aggregator.name}.{self._name}.direct_energy_exchanges", deepcopy(direct_exchanges[aggregator.superior.name]))
                else:
                    self._catalog.set(f"{aggregator.name}.{self._name}.direct_energy_exchanges", deepcopy(direct_exchanges[aggregator.superior.name]))

        return quantities_and_prices


    def top_down_phase(self, aggregator: "Aggregator"):  # todo à revoir dès avoir Gym + SB3 et PettingZoo + RLRay stable
        # Retrieving the energy accorded to each aggregator with the decision taken by the RL agent (scaled-up actions)
        [energy_accorded_to_consumers, energy_accorded_to_producers, energy_accorded_to_storage] = implement_my_interior_decision(self._name, self._catalog, aggregator)
        energy_accorded_to_exchange = implement_my_exchange_decision(self._name, self._catalog, aggregator)

        if f"{aggregator.name}.{self._name}.internal_decision" not in self._catalog.keys:  # scaled up actions (internal)
            self._catalog.add(f"{aggregator.name}.{self._name}.internal_decision", [energy_accorded_to_consumers, energy_accorded_to_producers, energy_accorded_to_storage])
        else:
            self._catalog.set(f"{aggregator.name}.{self._name}.internal_decision", [energy_accorded_to_consumers, energy_accorded_to_producers, energy_accorded_to_storage])

        if f"{aggregator.name}.{self._name}.exchange_decision" not in self._catalog.keys:  # scaled up actions (exchange)
            self._catalog.add(f"{aggregator.name}.{self._name}.exchange_decision", energy_accorded_to_exchange)
        else:
            self._catalog.set(f"{aggregator.name}.{self._name}.exchange_decision", energy_accorded_to_exchange)

        internal_buying_price, internal_selling_price = self._catalog.get(f"{aggregator.name}.{self._name}.energy_prices").values()
        maximum_energy_consumed, maximum_energy_produced = self._catalog.get(f"{aggregator.name}.{self._name}.energy_maximum_quantities").values()

        # Initialization
        energy_bought_outside = 0  # the absolute value of energy bought outside
        energy_sold_outside = 0  # the absolute value of energy sold outside
        energy_bought_inside = 0  # the absolute value of energy bought inside
        energy_sold_inside = 0  # the absolute value of energy sold inside

        money_earned_outside = 0  # the absolute value of money earned outside
        money_spent_outside = 0  # the absolute value of money spent outside
        money_earned_inside = 0  # the absolute value of money earned inside
        money_spent_inside = 0  # the absolute value of money spent inside

        [min_price, max_price] = self._limit_prices(aggregator)  # thresholds of accepted energy prices

        # Checking first the superior message
        if aggregator.superior not in self._catalog.get(f"{self._name}.strategy_scope"):
            old_energy_accorded_from_superior = self._catalog.get(f"{aggregator.name}.{aggregator.superior.nature.name}.energy_accorded")
            if not isinstance(old_energy_accorded_from_superior, list):
                for tup in energy_accorded_to_exchange.keys():
                    if aggregator.superior.name in tup:
                        old_energy_accorded_from_superior["quantity"] = - energy_accorded_to_exchange[tup] / aggregator.efficiency
                        if energy_accorded_to_exchange[tup] < 0:  # achat
                            old_energy_accorded_from_superior["price"] = min(old_energy_accorded_from_superior["price"], max_price)
                        else:
                            old_energy_accorded_from_superior["price"] = max(old_energy_accorded_from_superior["price"], min_price)
                        self._catalog.set(f"{aggregator.name}.{aggregator.superior.nature.name}.energy_accorded", old_energy_accorded_from_superior)
            else:
                for tup in energy_accorded_to_exchange.keys():
                    if aggregator.superior.name in tup:
                        if len(old_energy_accorded_from_superior) > 0:
                            old_energy_accorded_from_superior[0]["quantity"] = - energy_accorded_to_exchange[tup] / aggregator.efficiency
                        else:
                            old_energy_accorded_from_superior = [self._create_decision_message()]
                            old_energy_accorded_from_superior[0]["quantity"] = - energy_accorded_to_exchange[tup] / aggregator.efficiency
                            if energy_accorded_to_exchange[tup] < 0:  # achat
                                old_energy_accorded_from_superior[0]["price"] = min(max_price, old_energy_accorded_from_superior[0]["price"])
                            else:
                                old_energy_accorded_from_superior[0]["price"] = max(min_price, old_energy_accorded_from_superior[0]["price"])
                        self._catalog.set(f"{aggregator.name}.{aggregator.superior.nature.name}.energy_accorded", old_energy_accorded_from_superior)

        # Balance of the exchanges made with outside
        [money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside] = self._exchanges_balance(aggregator, money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside)


        # Internal balance
        [sorted_demands, sorted_offers, sorted_storage] = self._separe_quantities(aggregator)  # sorting the quantities
        if not self.optimized_distribution_flag:  # equal distribution
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

        else:  # GA-based distribution to individual energy systems inside each area/aggregator
            # The Emin are served first for all (except storage devices) - devices which don't provide flexibility (Emin = Emax) are not concerned by optimization (fully served)
            [sorted_demands, indirect_optimization_demands, energy_accorded_to_consumers, money_earned_inside, energy_sold_inside] = distribute_min_consumption(self, aggregator, internal_buying_price, sorted_demands, energy_accorded_to_consumers, money_earned_inside, energy_sold_inside)
            [sorted_offers, indirect_optimization_offers, energy_accorded_to_producers, money_spent_inside, energy_bought_inside] = distribute_min_production(self, aggregator, internal_selling_price, sorted_offers, - energy_accorded_to_producers, money_spent_inside, energy_bought_inside)
            indirect_optimization_storage = get_full_storage_message(self, aggregator, sorted_storage)

            # The distribution of energy is optimized for the remaining devices
            [sorted_demands, sorted_offers, sorted_storage] = optimized_sorting(indirect_optimization_demands, indirect_optimization_offers, indirect_optimization_storage,
                                                                                sorted_demands, sorted_offers, sorted_storage,
                                                                                energy_accorded_to_consumers, energy_accorded_to_producers, energy_accorded_to_storage,
                                                                                internal_buying_price, internal_selling_price,
                                                                                self.sorting_coefficients, compute_output)
            # determination of storage usage
            if energy_accorded_to_storage < 0:  # if the energy storage systems are discharging
                for message in sorted_storage:
                    self._transform_storage_into_production(message)
                [energy_accorded_to_storage, money_spent_inside, energy_bought_inside] = self._distribute_production_full_service(aggregator, internal_selling_price,
                                                                                                            sorted_storage, - energy_accorded_to_storage,
                                                                                                            money_spent_inside, energy_bought_inside)

            else:  # if they are charging
                for message in sorted_storage:
                    self._transform_storage_into_consumption(message)
                [energy_accorded_to_storage, money_earned_inside, energy_sold_inside] = self._distribute_consumption_full_service(aggregator, internal_buying_price,
                                                                                                            sorted_storage, energy_accorded_to_storage,
                                                                                                            money_earned_inside, energy_sold_inside)

            # then we distribute the remaining quantities according to our sort
            # distribution among consumptions
            [energy_accorded_to_consumers, money_earned_inside, energy_sold_inside] = self._distribute_consumption_full_service(aggregator, internal_buying_price,
                                                                                                            sorted_demands, energy_accorded_to_consumers,
                                                                                                            money_earned_inside, energy_sold_inside)
            # distribution among productions
            [energy_accorded_to_producers, money_spent_inside, energy_bought_inside] = self._distribute_production_full_service(aggregator, internal_selling_price,
                                                                                                             sorted_offers, energy_accorded_to_producers,
                                                                                                             money_spent_inside, energy_bought_inside)

        self._update_balances(aggregator, energy_bought_inside, energy_bought_outside, energy_sold_inside, energy_sold_outside, money_spent_inside, money_spent_outside, money_earned_inside, money_earned_outside, maximum_energy_consumed, maximum_energy_produced)


    def multi_energy_balance_check(self, aggregator):  # TODO - maybe to be modified to terminate the episode if "incompatibility"
        pass
