# Imports
from src.common.Strategy import Strategy
from lib.Subclasses.Strategy.DRLStrategy.DRL_Strategy_utilities import *
from lib.Subclasses.Strategy.SingleAgentDRLStrategy.Utilities import *


class SingleAgentDRLStrategy(Strategy):

    def __init__(self, name=None, optional_params=None, red_dof_flag=False):
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

        # In case we remove 1-degree of freedom per aggregator
        self.red_dof_flag = red_dof_flag

        # For the second update in case for converters both ends take a decision
        self._second_call = False

    # ##################################################################################################################
    # Dynamic behavior
    ####################################################################################################################

    def bottom_up_phase(self, aggregator: "Aggregator"):

        # In case of 2nd call to aggregator.ask() -> strategy.bottom_up_phase() after aggregator.check()
        if self._second_call:
            return self._catalog.get(f"{aggregator.name}.{aggregator.superior.nature.name}.energy_wanted")

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
        conversion_consumptions, conversion_productions = correction_to_formalism(converter_message[aggregator.name]["Energy_Conversion"])

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
            formalism_message['Energy_Consumption']["energy_maximum"] = maximum_energy_consumed - conversion_consumptions
            formalism_message['Energy_Production']["energy_minimum"] = - minimum_energy_produced
            formalism_message['Energy_Production']["energy_maximum"] = - (maximum_energy_produced + conversion_productions)
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

        # In case of 2nd call to aggregator.distribute() -> strategy.top_down_phase() after aggregator.check()
        if self._second_call:
            self._second_call = False  # resetting the flag for next 'normal' call

            # Initialization
            energy_bought_outside = self._catalog.get(f"{aggregator.name}.energy_bought")['outside']
            energy_bought_inside = self._catalog.get(f"{aggregator.name}.energy_bought")['inside']
            energy_sold_outside = self._catalog.get(f"{aggregator.name}.energy_sold")['outside']
            energy_sold_inside = self._catalog.get(f"{aggregator.name}.energy_sold")['inside']
            money_earned_outside = self._catalog.get(f"{aggregator.name}.money_earned")['outside']
            money_earned_inside = self._catalog.get(f"{aggregator.name}.money_earned")['inside']
            money_spent_outside = self._catalog.get(f"{aggregator.name}.money_spent")['outside']
            money_spent_inside = self._catalog.get(f"{aggregator.name}.money_spent")['inside']

            maximum_energy_consumed, maximum_energy_produced = self._catalog.get(f"{aggregator.name}.{self._name}.energy_maximum_quantities").values()

            offset_dict, conso_dict, prod_dict = self._catalog.get(f"{aggregator.name}.{self._name}.converters_offset")

            # the energy excess/deficit of consumption/production is absorbed by energy exchange with superior
            old_energy_accorded_from_superior = self._catalog.get(f"{aggregator.name}.{aggregator.superior.nature.name}.energy_accorded")
            if isinstance(old_energy_accorded_from_superior, list):
                if len(old_energy_accorded_from_superior) > 0:  # if the superior aggregator has the same energy carrier
                    if old_energy_accorded_from_superior[0]['quantity'] > 0:
                        money_spent_outside -= old_energy_accorded_from_superior[0]['quantity'] * old_energy_accorded_from_superior[0]['price']
                        energy_bought_outside -= old_energy_accorded_from_superior[0]['quantity'] * aggregator.efficiency
                    else:
                        money_earned_outside -= abs(old_energy_accorded_from_superior[0]['quantity']) * old_energy_accorded_from_superior[0]['price']
                        energy_sold_outside -= abs(old_energy_accorded_from_superior[0]['quantity']) * aggregator.efficiency
                    old_energy_accorded_from_superior[0]['quantity'] -= (sum(conso_dict.values()) + sum(prod_dict.values())) / aggregator.efficiency
                else:  # if the aggregator has to make the balance inside by itself
                    deficit_to_manage = conso_dict["excess"] + prod_dict["deficit"]  # < 0 surplus of production / reduction of consumption needed
                    excess_to_manage = conso_dict["deficit"] + prod_dict["excess"]  # > 0 reduction of production / surplus of consumption needed
                    # todo patchwork solution for the MEG MARL case study - the incinerator absorbs the offset
                    energy_produced = self._catalog.get("Waste_to_heat.LTH.energy_accorded")
                    energy_produced["quantity"] += excess_to_manage + deficit_to_manage
                    self._catalog.set("Waste_to_heat.LTH.energy_accorded", energy_produced)
            else:
                if old_energy_accorded_from_superior['quantity'] > 0:
                    money_spent_outside -= old_energy_accorded_from_superior['quantity'] * old_energy_accorded_from_superior['price']
                    energy_bought_outside -= old_energy_accorded_from_superior['quantity'] * aggregator.efficiency
                else:
                    money_earned_outside -= abs(old_energy_accorded_from_superior['quantity']) * old_energy_accorded_from_superior['price']
                    energy_sold_outside -= abs(old_energy_accorded_from_superior['quantity']) * aggregator.efficiency
                old_energy_accorded_from_superior['quantity'] -= (sum(conso_dict.values()) + sum(prod_dict.values())) / aggregator.efficiency
            self._catalog.set(f"{aggregator.name}.{aggregator.superior.nature.name}.energy_accorded", old_energy_accorded_from_superior)
            # updating external balance
            [money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside] = self._exchanges_balance(aggregator, money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside)

            # Re-updating the internal and external balances
            self._update_balances(aggregator, energy_bought_inside, energy_bought_outside, energy_sold_inside, energy_sold_outside, money_spent_inside, money_spent_outside, money_earned_inside, money_earned_outside, maximum_energy_consumed, maximum_energy_produced)
            return

        # Retrieving the energy accorded to each aggregator with the decision taken by the RL agent (scaled-up actions)
        [energy_accorded_to_consumers, energy_accorded_to_producers, energy_accorded_to_storage] = implement_my_interior_decision(self._name, self._catalog, aggregator, self.red_dof_flag)
        energy_accorded_to_exchange = implement_my_exchange_decision(self._name, self._catalog, aggregator, self.red_dof_flag)
        if self.red_dof_flag:  # in case of reducing one degree of freedom, we complete the decision here
            energy_accorded_to_consumers, energy_accorded_to_producers, energy_accorded_to_storage, energy_accorded_to_exchange = complete_reduced_action(energy_accorded_to_consumers, energy_accorded_to_producers, energy_accorded_to_storage, energy_accorded_to_exchange, self._catalog, aggregator)

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

        # I.- External balance
        # Checking first the superior message (subaggregators are counted with the internal devices)
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

        # Balance of the exchanges made with outside (superior, since subaggregators are counted with internal devices)
        [money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside] = self._exchanges_balance(aggregator, money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside)

        # II.- Internal balance
        [sorted_demands, sorted_offers, sorted_storage] = self._separe_quantities(aggregator)  # sorting the quantities

        # 1) Deciding the energy flow values for converters
        [sorted_demands, sorted_offers, converters] = self._isolate_conversion_systems(sorted_demands, sorted_offers)
        [money_spent_inside, energy_bought_inside, money_earned_inside, energy_sold_inside] = self._serve_energy_conversion(aggregator, converters, energy_accorded_to_exchange, money_spent_inside, energy_bought_inside, money_earned_inside, energy_sold_inside, min_price, max_price, internal_buying_price, internal_selling_price)

        # 2) The energy flow values are then decided for the internal devices (consumers, producers and storage)
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
        energy_bought_dict = self._catalog.get(f"{aggregator.name}.energy_bought")
        energy_bought_outside = energy_bought_dict["outside"]
        energy_bought_inside = energy_bought_dict["inside"]

        energy_sold_dict = self._catalog.get(f"{aggregator.name}.energy_sold")
        energy_sold_outside = energy_sold_dict["outside"]
        energy_sold_inside = energy_sold_dict["inside"]

        money_spent_dict = self._catalog.get(f"{aggregator.name}.money_spent")
        money_spent_outside = money_spent_dict["outside"]
        money_spent_inside = money_spent_dict["inside"]

        money_earned_dict = self._catalog.get(f"{aggregator.name}.money_earned")
        money_earned_outside = money_earned_dict["outside"]
        money_earned_inside = money_earned_dict["inside"]

        # getting the old decision w.r.t energy exchanges with superior, subaggregators and converters
        Eexch_old = self._catalog.get(f"{aggregator.name}.{self._name}.exchange_decision")

        # getting the offset between the old decision and the energy accorded to converters after second update
        [sorted_demands, sorted_offers, sorted_storage] = self._separe_quantities(aggregator)
        [sorted_demands, sorted_offers, converters] = self._isolate_conversion_systems(sorted_demands, sorted_offers)
        [offset_dict, conso_offset, prod_offset, money_spent_inside, energy_bought_inside, money_earned_inside, energy_sold_inside] = self._identify_converter_offset(aggregator, converters, Eexch_old, money_spent_inside, energy_bought_inside, money_earned_inside, energy_sold_inside)
        if f"{aggregator.name}.{self._name}.converters_offset" not in self._catalog.keys:
            self._catalog.add(f"{aggregator.name}.{self._name}.converters_offset", [offset_dict, conso_offset, prod_offset])
        else:
            self._catalog.set(f"{aggregator.name}.{self._name}.converters_offset", [offset_dict, conso_offset, prod_offset])

        if abs(energy_bought_outside + energy_bought_inside - (energy_sold_outside + energy_sold_inside)) >= 1e-6:  # if balances do not match, a second round of distribution is performed
            self._catalog.set(f"{aggregator.name}.incompatibility", True)
            self._second_call = True

        energy_bought_dict["inside"] = energy_bought_inside
        energy_sold_dict["inside"] = energy_sold_inside
        money_spent_dict["inside"] = money_spent_inside
        money_earned_dict["inside"] = money_earned_inside
        self._catalog.set(f"{aggregator.name}.energy_bought", energy_bought_dict)
        self._catalog.set(f"{aggregator.name}.energy_sold", energy_sold_dict)
        self._catalog.set(f"{aggregator.name}.money_spent", money_spent_dict)
        self._catalog.set(f"{aggregator.name}.money_earned", money_earned_dict)

    # #################################################################################################################
    # Strategy blocks
    # #################################################################################################################

    def _limit_quantities(self, aggregator: "Aggregator",
                          minimum_energy_consumed: float, maximum_energy_consumed: float,
                          minimum_energy_produced: float, maximum_energy_produced: float,
                          maximum_energy_charge: float, maximum_energy_discharge: float):  # compute the minimum an maximum quantities of energy needed to be consumed and produced locally
        energy_stored = 0  # kWh
        energy_storable = 0  # kWh

        # quantities concerning devices
        for device_name in aggregator.devices:
            if isinstance(self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted"), dict):
                message = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")
            else:  # for dummy converters (with the same energy nature)
                for element in self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted"):
                    if element['aggregator'] == aggregator.name:
                        message = element
                        break
            energy_minimum = message["energy_minimum"]  # the minimum quantity of energy asked
            energy_nominal = message["energy_nominal"]  # the nominal quantity of energy asked
            energy_maximum = message["energy_maximum"]  # the maximum quantity of energy asked

            # balances
            if message["type"] == "storage" and energy_minimum < 0 < energy_maximum:  # it is both consumer and producer
                # storage
                maximum_energy_charge += energy_maximum
                maximum_energy_discharge -= energy_minimum
                energy_stored += message["state_of_charge"] * message["capacity"]
                energy_storable += (1 - message["state_of_charge"]) * message["capacity"]

            elif energy_maximum > 0:  # the device wants to consume energy
                if energy_nominal == energy_maximum:  # if it is urgent
                    minimum_energy_consumed += energy_maximum

                else:  # if there is a minimum
                    minimum_energy_consumed += energy_minimum
                maximum_energy_consumed += energy_maximum

            elif energy_maximum < 0:  # the device wants to sell energy
                if energy_nominal == energy_maximum:  # if it is urgent
                    minimum_energy_produced -= energy_maximum
                else:
                    minimum_energy_produced -= energy_minimum
                maximum_energy_produced -= energy_maximum

        # quantities concerning subaggregators
        for subaggregator in aggregator.subaggregators:  # quantities concerning aggregators
            quantities_and_prices = self._catalog.get(f"{subaggregator.name}.{aggregator.nature.name}.energy_wanted")

            for element in quantities_and_prices:
                energy_minimum = element["energy_minimum"]  # the minimum quantity of energy asked
                energy_nominal = element["energy_nominal"]  # the nominal quantity of energy asked
                energy_maximum = element["energy_maximum"]  # the maximum quantity of energy asked

                # balances
                if energy_maximum > 0:  # the device wants to consume energy
                    if energy_nominal == energy_maximum:  # if it is urgent
                        minimum_energy_consumed += energy_maximum

                    else:  # if there is a minimum
                        minimum_energy_consumed += energy_minimum
                    maximum_energy_consumed += energy_maximum

                elif energy_maximum < 0:  # the device wants to sell energy
                    if energy_nominal == energy_maximum:  # if it is urgent
                        minimum_energy_produced -= energy_maximum
                    else:
                        minimum_energy_produced -= energy_minimum
                    maximum_energy_produced -= energy_maximum

        # decision-making values recording
        self._catalog.set(f"{aggregator.name}.minimum_energy_consumption", minimum_energy_consumed)
        self._catalog.set(f"{aggregator.name}.maximum_energy_consumption", maximum_energy_consumed)
        self._catalog.set(f"{aggregator.name}.minimum_energy_production", minimum_energy_produced)
        self._catalog.set(f"{aggregator.name}.maximum_energy_production", maximum_energy_produced)
        self._catalog.set(f"{aggregator.name}.energy_stored", energy_stored)
        self._catalog.set(f"{aggregator.name}.energy_storable", energy_storable)

        return [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, maximum_energy_charge, maximum_energy_discharge]

    def _separe_quantities(self, aggregator: "Aggregator") -> List[List]:  # a function calculating the emergency associated, without sort, with devices and returning 2 sorted lists: one for the demands and one for the offers
        sorted_demands = []  # a list where the demands of energy are gathered
        sorted_offers = []  # a list where the offers of energy are gathered
        sorted_storage = []  # a list where the offers of storage are gathered

        for device_name in aggregator.devices:  # if there is missing energy
            if isinstance(self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted"), dict):
                Emin = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]
                Enom = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["energy_nominal"]
                Emax = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]
                price = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["price"]
                device_type = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["type"]
            else:
                for element in self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted"):
                    if element['aggregator'] == aggregator.name:
                        Emin = element["energy_minimum"]
                        Enom = element["energy_nominal"]
                        Emax = element["energy_maximum"]
                        price = element["price"]
                        device_type = element["type"]
                        break

            if Emax == Emin:  # if the min energy is equal to the maximum, it means that this quantity is necessary
                emergency = 1  # an indicator of how much the quantity is urgent
            else:
                emergency = (Enom - Emin) / (Emax - Emin)  # an indicator of how much the quantity is urgent

            if device_type == "storage" and Emin < 0 < Emax:  # it is both consumer and producer
                message = self._create_empty_sorted_lists()
                message["emergency"] = 0
                message["quantity"] = Emax
                message["quantity_min"] = Emin
                message["price"] = price
                message["name"] = device_name
                message["type"] = "storage"
                sorted_storage.append(message)
            elif Emax > 0:  # if the energy is strictly positive, it means that the device or the aggregator is asking for energy
                message = self._create_empty_sorted_lists()
                message["emergency"] = emergency
                message["quantity"] = Emax
                message["quantity_min"] = Emin
                message["price"] = price
                message["name"] = device_name
                message["type"] = "consumption" if not device_type == "converter" else device_type
                sorted_demands.append(message)
            elif Emax < 0:  # if the energy is strictly negative, it means that the device or the aggregator is proposing energy
                message = self._create_empty_sorted_lists()
                message["emergency"] = emergency
                message["quantity"] = Emax
                message["quantity_min"] = Emin
                message["price"] = price
                message["name"] = device_name
                message["type"] = "production" if not device_type == "converter" else device_type
                sorted_offers.append(message)
            # if the energy = 0, then there is no need to add it to one of the list

        for subaggregator in aggregator.subaggregators:
            quantities_and_prices = self._catalog.get(f"{subaggregator.name}.{aggregator.nature.name}.energy_wanted")

            for element in quantities_and_prices:
                Emin = element["energy_minimum"]  # the minimum quantity of energy asked
                Enom = element["energy_nominal"]  # the nominal quantity of energy asked
                Emax = element["energy_maximum"]  # the maximum quantity of energy asked
                price = element["price"]

                if Emax == Emin:  # if the min energy is equal to the maximum, it means that this quantity is necessary
                    emergency = 1  # an indicator of how much the quantity is urgent
                else:
                    emergency = (Enom - Emin) / (Emax - Emin)  # an indicator of how much the quantity is urgent

                if Emax > 0:  # if the energy is strictly positive, it means that the device or the aggregator is asking for energy
                    message = self._create_empty_sorted_lists()
                    message["emergency"] = emergency
                    message["quantity"] = Emax
                    message["quantity_min"] = Emin
                    message["price"] = price
                    message["name"] = subaggregator.name
                    sorted_demands.append(message)
                elif Emax < 0:  # if the energy is strictly negative, it means that the device or the aggregator is proposing energy
                    message = self._create_empty_sorted_lists()
                    message["emergency"] = emergency
                    message["quantity"] = Emax
                    message["quantity_min"] = Emin
                    message["price"] = price
                    message["name"] = subaggregator.name
                    sorted_offers.append(message)

        return [sorted_demands, sorted_offers, sorted_storage]

    # #################################################################################################################
    # emergency distribution functions
    ###################################################################################################################

    def _serve_emergency_demands(self, aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
        lines_to_remove = []  # a list containing the number of lines having to be removed
        for i in range(len(sorted_demands)):  # demands
            energy = sorted_demands[i]["quantity"]

            name = sorted_demands[i]["name"]
            price = sorted_demands[i]["price"]
            price = min(price, max_price)

            if sorted_demands[i]["emergency"] == 1:  # if it is urgent
                lines_to_remove.append(i)

                if energy > energy_available_consumption:  # if the quantity demanded is superior to the rest of energy available
                    energy = energy_available_consumption  # it is served partially, even if it is urgent

                message = self._create_decision_message()
                message["quantity"] = energy
                message["price"] = price

                if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                else:  # if it is a device
                    quantities_given = message

                self._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

                energy_available_consumption -= energy
                money_earned_inside += energy * price  # money earned by selling energy to the device
                energy_sold_inside += energy  # the absolute value of energy sold inside

            else:
                energy_minimum = sorted_demands[i]["quantity_min"]  # the minimum quantity of energy asked
                energy_maximum = sorted_demands[i]["quantity"]  # the maximum quantity of energy asked

                if energy_minimum > energy_available_consumption:  # if the quantity demanded is superior to the rest of energy available
                    energy = energy_available_consumption  # it is served partially, even if it is urgent
                else:
                    energy = energy_minimum

                message = self._create_decision_message()
                message["quantity"] = energy
                message["price"] = price

                if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                    sorted_demands[i]["quantity_min"] = 0
                    sorted_demands[i]["quantity"] = energy_maximum-energy_minimum  # the need is updated
                else:  # if it is a device
                    quantities_given = message

                if isinstance(self._catalog.get(f"{name}.{aggregator.nature.name}.energy_wanted"), dict):  # for normal devices
                    self._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served
                else:  # for dummy converters (with the same energy nature)
                    dummy_message = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    idx = dummy_message['aggregator'].index(aggregator.name)
                    dummy_message['quantity'][idx] = message["quantity"]
                    dummy_message['price'][idx] = message["price"]
                    self._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", dummy_message)  # it is served

                energy_available_consumption -= energy
                money_earned_inside += energy * price  # money earned by selling energy to the device
                energy_sold_inside += energy  # the absolute value of energy sold inside
                sorted_demands[i]["quantity"] = energy_maximum - energy

        lines_to_remove.reverse()  # we reverse the list, otherwise the indices will move during the deletion
        for line_index in lines_to_remove:  # removing the already served elements
            sorted_demands.pop(line_index)

        return [sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside]

    def _distribute_consumption_partial_service(self, aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):  # distribution among consumptions
        energy_total = 0

        for element in sorted_demands:  # we sum all the emergency and the energy of demands1
            energy_total += element["quantity"]

        if energy_total != 0:

            energy_ratio = min(1, energy_available_consumption / energy_total)  # the average rate of satisfaction, cannot be superior to 1

            for demand in sorted_demands:  # then we distribute a bit of energy to all demands
                name = demand["name"]
                energy = demand["quantity"]  # the quantity of energy needed
                price = demand["price"]  # the price of energy
                price = min(price, max_price)
                energy *= energy_ratio

                Emin = demand["quantity_min"]  # we get back the minimum, which has already been served
                message = self._create_decision_message()
                message["quantity"] = Emin + energy
                message["price"] = price
                if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                else:  # if it is a device
                    quantities_given = message
                if isinstance(self._catalog.get(f"{name}.{aggregator.nature.name}.energy_wanted"), dict):  # for normal devices
                    self._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served
                else:  # for dummy converters (with the same energy nature)
                    dummy_message = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    idx = dummy_message['aggregator'].index(aggregator.name)
                    dummy_message['quantity'][idx] = message["quantity"]
                    dummy_message['price'][idx] = message["price"]
                    self._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", dummy_message)  # it is served

                money_earned_inside += energy * price  # money earned by selling energy to the subaggregator
                energy_sold_inside += energy  # the absolute value of energy sold inside
                energy_available_consumption -= energy

        return [energy_available_consumption, money_earned_inside, energy_sold_inside]

    def _distribute_production_partial_service(self, aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float, energy_bought_inside: float):
        # distribution among productions
        energy_total = 0

        for element in sorted_offers:  # we sum all the emergency and the energy of offers
            energy_total -= element["quantity"]

        if energy_total != 0:

            energy_ratio = min(1, energy_available_production / energy_total)  # the average rate of satisfaction, cannot be superior to 1

            for offer in sorted_offers:  # then we distribute a bit of energy to all offers
                name = offer["name"]
                energy = offer["quantity"]  # the quantity of energy needed
                price = offer["price"]  # the price of energy
                price = max(price, min_price)
                energy *= energy_ratio

                Emin = offer["quantity_min"]  # we get back the minimum, which has already been served
                message = self._create_decision_message()
                message["quantity"] = Emin + energy
                message["price"] = price
                if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                else:  # if it is a device
                    quantities_given = message

                if isinstance(self._catalog.get(f"{name}.{aggregator.nature.name}.energy_wanted"), dict):  # for normal devices
                    self._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served
                else:  # for dummy converters (with the same energy nature)
                    dummy_message = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    idx = dummy_message['aggregator'].index(aggregator.name)
                    dummy_message['quantity'][idx] = message["quantity"]
                    dummy_message['price'][idx] = message["price"]
                    self._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", dummy_message)  # it is served

                money_spent_inside -= energy * price  # money earned by selling energy to the subaggregator
                energy_bought_inside -= energy  # the absolute value of energy sold inside
                energy_available_production += energy

        return [energy_available_production, money_spent_inside, energy_bought_inside]

    # #################################################################################################################
    # energy conversion devices specific functions
    ###################################################################################################################
    def _isolate_conversion_systems(self, sorted_demands: List[Dict], sorted_offers: List[Dict]):
        """
        This method is used to isolate the converter devices from the other internal devices.
        """
        my_condition = lambda x: x['type'] == "converter"
        moved = list(filter(my_condition, sorted_demands))
        moved.extend(list(filter(my_condition, sorted_offers)))
        sorted_demands = list(filter(lambda x: not my_condition(x), sorted_demands))
        sorted_offers = list(filter(lambda x: not my_condition(x), sorted_offers))

        return sorted_demands, sorted_offers, moved

    def _serve_energy_conversion(self, aggregator: "Aggregator", converters: List[Dict], energy_exchange_dict: Dict, money_spent_inside: float, energy_bought_inside: float, money_earned_inside: float, energy_sold_inside: float, min_price: float, max_price: float, internal_buying_price: float, internal_selling_price: float):
        """
        This method is used to attribute energy to conversion systems.
        """
        for element in converters:
            for exchange in energy_exchange_dict:
                if element['name'] in exchange:
                    energy_to_attribute = energy_exchange_dict[exchange]
                    if energy_to_attribute < 0:  # energy offer/supply
                        energy_bought_inside += abs(energy_to_attribute)
                        price = max(min_price, internal_selling_price)
                        money_spent_inside += abs(energy_bought_inside) * price
                    else:  # energy demand/consumption
                        energy_sold_inside += energy_to_attribute
                        price = min(max_price, internal_buying_price)
                        money_earned_inside += energy_to_attribute * price

                    og_msg = self._catalog.get(f"{element['name']}.{aggregator.nature.name}.energy_accorded")
                    if isinstance(og_msg['quantity'], list):  # for dummy converters (with the same energy nature)
                        my_idx = og_msg["aggregator"].index(aggregator.name)
                        og_msg['quantity'][my_idx] = energy_to_attribute
                        og_msg['price'][my_idx] = price
                        self._catalog.set(f"{element['name']}.{aggregator.nature.name}.energy_accorded", og_msg)
                    else:  # for normal converter (with different energy natures)
                        og_msg['quantity'] = energy_to_attribute
                        og_msg['price'] = price
                        self._catalog.set(f"{element['name']}.{aggregator.nature.name}.energy_accorded", og_msg)
                    break

        return money_spent_inside, energy_bought_inside, money_earned_inside, energy_sold_inside

    def _identify_converter_offset(self, aggregator: "Aggregator", converters: List[Dict], old_decision: Dict, money_spent_inside: float, energy_bought_inside: float, money_earned_inside: float, energy_sold_inside: float):
        """
        This helper function is used in the 2nd top down phase call.
        It is used to calculate the difference between the original decision w.r.t converters & their second update.
        """
        offset = {}
        conso_plus = 0.0
        conso_minus = 0.0
        prod_plus = 0.0
        prod_minus = 0.0

        for element in converters:
            for exchange in old_decision:
                if element['name'] in exchange:
                    old_exch = old_decision[exchange]
                    acc_msg = self._catalog.get(f"{element['name']}.{aggregator.nature.name}.energy_accorded")
                    if isinstance(acc_msg['quantity'], list):  # for dummy converters (same energy carrier)
                        my_idx = acc_msg["aggregator"].index(aggregator.name)
                        offset[element['name']] = old_exch - acc_msg["quantity"][my_idx]
                        price = acc_msg["price"][my_idx]
                    else:  # for normal converters
                        offset[element['name']] = old_exch - acc_msg["quantity"]
                        price = acc_msg["price"]

                    if old_exch > 0 and offset[element['name']] < 0:
                        conso_plus += offset[element['name']]
                        energy_sold_inside += abs(offset[element['name']])
                        money_earned_inside += abs(offset[element['name']]) * price
                    elif old_exch > 0 and offset[element['name']] > 0:
                        conso_minus += offset[element['name']]
                        energy_sold_inside -= abs(offset[element['name']])
                        money_earned_inside -= abs(offset[element['name']]) * price
                    elif old_exch < 0 and offset[element['name']] < 0:
                        prod_minus += offset[element['name']]
                        energy_bought_inside -= abs(offset[element['name']])
                        money_spent_inside -= abs(offset[element['name']]) * price
                    elif old_exch < 0 and offset[element['name']] > 0:
                        prod_plus += offset[element['name']]
                        energy_bought_inside += abs(offset[element['name']])
                        money_spent_inside += abs(offset[element['name']]) * price


        consumption_offset = {"deficit": conso_minus, "excess": conso_plus}
        production_offset = {"deficit": prod_minus, "excess": prod_plus}

        return offset, consumption_offset, production_offset, money_spent_inside, energy_bought_inside, money_earned_inside, energy_sold_inside
