from lib.Subclasses.Strategy.TrainingStrategy.TrainingStrategy import TrainingStrategy
from typing import List, Dict, Tuple, Callable
import pandas as pd


class MLStrategy(TrainingStrategy):
    def __init__(self, priorities_consumption: Callable, priorities_production: Callable):
        super().__init__(priorities_consumption, priorities_production)

        index = ["min"]
        columns = ["assess", "exchange", "distribute"]
        data = [[assess_min_conso, exchanges_min_conso, distribution_min_conso]
                ]
        self._options_consumption = pd.DataFrame(index=index, columns=columns, data=data)

        index = ["min"]
        columns = ["assess", "exchange", "distribute"]
        data = [[assess_min_prod, exchanges_min_conso, distribution_min_prod]
                ]
        self._options_production = pd.DataFrame(index=index, columns=columns, data=data)

    def add_consumption_options(self, consumption_dataframe: pd.DataFrame):
        """
        This function completes the standard list of options available for consumption.

        Parameters
        ----------
        consumption_dataframe: Dataframe, a dataframe built as followed:
        - columns are "assess", "exchange" and "distribute"
        - the index is a list of strings
        - the data is composed of functions managing the options
        """

        self._options_consumption = self._options_consumption.append(consumption_dataframe)

    def add_production_options(self, production_dataframe: pd.DataFrame):
        """
        This function completes the standard list of options available for production.

        Parameters
        ----------
        production_dataframe: Dataframe, a dataframe built as followed:
        - columns are "assess", "exchange" and "distribute"
        - the index is a list of strings
        - the data is composed of functions managing the options
        """

        self._options_production = self._options_production.append(production_dataframe)

    # ##########################################################################################
    # Priorities functions
    # ##########################################################################################

    def _asses_quantities_for_each_option(self, aggregator: "Aggregator") -> Dict:
        [demands, offers] = self._sort_quantities(aggregator, self._sort_function)
        quantity_per_option = {"consumption": {}, "production": {}}
        priorities_consumption = self._get_priorities_consumption()
        priorities_production = self._get_priorities_production()

        for priority in priorities_consumption:
            quantity_per_option["consumption"][priority] = self._options_consumption.loc[priority]["assess"](self, aggregator, demands)
        for priority in priorities_production:
            quantity_per_option["production"][priority] = self._options_production.loc[priority]["assess"](self, aggregator, offers)

        # balances update
        min_cons = quantity_per_option["consumption"]["min"]
        min_prod = quantity_per_option["production"]["min"]
        max_cons = sum(quantity_per_option["consumption"].values()) - min_cons
        max_prod = sum(quantity_per_option["production"].values()) - min_prod
        self._catalog.set(f"{aggregator.name}.minimum_energy_consumption", min_cons)
        self._catalog.set(f"{aggregator.name}.maximum_energy_consumption", max_cons)
        self._catalog.set(f"{aggregator.name}.minimum_energy_production", min_prod)
        self._catalog.set(f"{aggregator.name}.maximum_energy_production", max_prod)

        return quantity_per_option

    def _apply_priorities_exchanges(self, aggregator: "Aggregator", quantity_to_affect: float,
                                    quantity_available_per_option: Dict) -> List[Dict]:
        quantities_and_price = []
        priorities_consumption = self._get_priorities_consumption()
        priorities_production = self._get_priorities_production()

        for priority in priorities_consumption:
            quantity_available = quantity_available_per_option["consumption"][priority]
            quantity_affected, quantities_and_price = self._options_consumption.loc[priority]["exchange"](self, aggregator,
                                                                                                          quantity_to_affect,
                                                                                                          quantity_available,
                                                                                                          quantities_and_price)
            quantity_to_affect -= quantity_affected
        for priority in priorities_production:
            quantity_available = quantity_available_per_option["production"][priority]
            quantity_affected, quantities_and_price = self._options_production.loc[priority]["exchange"](self, aggregator,
                                                                                                         quantity_to_affect,
                                                                                                         quantity_available,
                                                                                                         quantities_and_price)
            quantity_to_affect -= quantity_affected

        return quantities_and_price

    def _apply_priorities_distribution(self, aggregator: "Aggregator", min_price: float, max_price: float,
                                       sorted_demands,
                                       sorted_offers, energy_available_consumption: float,
                                       energy_available_production: float) -> Tuple:
        energy_bought_inside = 0  # the absolute value of energy bought inside
        energy_sold_inside = 0  # the absolute value of energy sold inside
        money_earned_inside = 0  # the absolute value of money earned inside
        money_spent_inside = 0  # the absolute value of money spent inside
        priorities_consumption = self._get_priorities_consumption()
        priorities_production = self._get_priorities_production()

        for priority in priorities_consumption:
            [sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside] = self._options_consumption.loc[priority]["distribute"](self, aggregator, min_price, sorted_demands, energy_available_production, money_spent_inside, energy_bought_inside)
        for priority in priorities_production:
            [sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside] = self._options_production.loc[priority]["distribute"](self, aggregator, max_price, sorted_offers, energy_available_consumption, money_earned_inside, energy_sold_inside)
        return energy_bought_inside, energy_sold_inside, money_spent_inside, money_earned_inside

# ################################################################################################################
# min management
# ################################################################################################################
# min prod


def assess_min_prod(strategy: "Strategy", aggregator: "Aggregator", offers: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in offers:
        quantity_for_this_option -= demand["quantity_min"]

    return quantity_for_this_option


def exchanges_min_prod(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float,
                       quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    quantity_to_affect = - max(0, quantity_to_affect - quantity_available_for_this_option)
    return quantity_to_affect, quantities_and_prices


# no specific function for distribution, the canonical one is used
def distribution_min_prod(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
    return strategy._serve_emergency_offers(aggregator, max_price, sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside)


# min consumption
def assess_min_conso(strategy: "Strategy", aggregator: "Aggregator", demands: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in demands:
        quantity_for_this_option += demand["quantity_min"]

    return quantity_for_this_option


def exchanges_min_conso(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    quantity_to_affect = max(0, quantity_to_affect - quantity_available_for_this_option)
    return quantity_to_affect, quantities_and_prices


# no specific function for distribution, the canonical one is used
def distribution_min_conso(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
    return strategy._serve_emergency_demands(aggregator, max_price, sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside)

