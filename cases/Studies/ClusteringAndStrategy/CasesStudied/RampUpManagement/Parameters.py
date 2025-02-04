from random import seed
import numpy as np
import itertools


from cases.Studies.ClusteringAndStrategy.Utilities import *

# ######################################################################################################################
# hyperparameters - todo à confirmer avec Timothé
# ######################################################################################################################
training_simulation_length = 24  # length of sequences used for clustering.
sequences_number = 365  # number of sequences simulated
gap = 24  # gap (given in iterations) between 2 sequences simulated
cluster_number = 35  # the number of clusters, fixed arbitrarily, can be determined studying the dispersion inside each cluster (see elbow method)


random_seed = "tournesol"  # random seed is set to have always the same result for 1 given set of parameters
seed(random_seed)


comparison_simulation_length = 8760  # length of the final run aimed at evaluating the efficiency of the strategy


# ######################################################################################################################
# metrics - todo à confirmer avec Timothé
# ######################################################################################################################
clustering_metrics = [  # prices are not taken into account for now
    # storage
    # "DHN_pipelines.energy_stored",
    # consumption
    "old_house.LTH.energy_bought",
    "new_house.LTH.energy_bought",
    "office.LTH.energy_bought",
    # production
    "incinerator.LTH.energy_sold",
    "fast_gas_boiler.LTH.energy_sold",
]  # métriques utilisées au moment de la définition des clusters, spécifiques au cas étudié...

performance_metrics = [
    "DHN_manager.money_earned",
    "DHN_manager.money_spent",

    # "DHN_pipelines.LTH.energy_bought",
    # "DHN_pipelines.LTH.energy_sold",

    "old_house.LTH.energy_bought",
    "old_house.LTH.energy_sold",
    "new_house.LTH.energy_bought",
    "new_house.LTH.energy_sold",
    "office.LTH.energy_bought",
    "office.LTH.energy_sold",

    "DHN_manager.LTH.energy_bought",
    "DHN_manager.LTH.energy_sold",
    "DHN_manager.LVE.energy_sold",
    "DHN_manager.LVE.energy_bought",

    "incinerator.LTH.energy_sold",
    "fast_gas_boiler.LTH.energy_sold",

    "district_heating_grid.energy_sold",
    "district_heating_grid.energy_bought",
]  # critères de performance, spécifiques au cas étudié...

coef = 1

def performance_norm(performance_vector: Dict) -> float:
    return (sum(performance_vector["incinerator.LTH.energy_sold"]) - sum(performance_vector["fast_gas_boiler.LTH.energy_sold"])) * coef


# ######################################################################################################################
# strategies, defined as an ordered list of the available levers - todo à confirmer avec Timothé
# ######################################################################################################################

# consumption_options = ["heat_loads", "charging_storage", "nothing"]
# production_options = ["heat_baseload", "heat_peakload", "discharging_storage"]
consumption_options = ["heat_loads", "nothing"]
production_options = ["heat_baseload", "heat_peakload"]
assessed_priorities_consumption = [list(toto) for toto in itertools.permutations(consumption_options)]
assessed_priorities_production = [list(toto) for toto in itertools.permutations(production_options)]
assessed_priorities = {"consumption": assessed_priorities_consumption, "production": assessed_priorities_production}


# reference strategies
def ref_priorities_consumption(strategy: "Strategy"):
    # return ["heat_loads", "charging_storage", "nothing"]
    return ["heat_loads", "nothing"]


def ref_priorities_production(strategy: "Strategy"):
    # return ["heat_baseload", "discharging_storage", "heat_peakload"]
    return ["heat_baseload", "heat_peakload"]
