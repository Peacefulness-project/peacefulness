from random import seed
import numpy as np
import itertools


from cases.Studies.ClusteringAndStrategy.Utilities import *

# ######################################################################################################################
# hyperparameters -
# ######################################################################################################################
training_simulation_length = 8760  # length of sequences used for clustering.
clustering_sequences_number = 1  # number of sequences simulated
gap = 1  # gap (given in iterations) between 2 sequences simulated


comparison_simulation_length = 8760  # length of the final run aimed at evaluating the efficiency of the strategy


# ######################################################################################################################
# metrics
# ######################################################################################################################
clustering_metrics = [  # prices are not taken into account for now
    "residential_dwellings.LVE.energy_erased", "industrial_process.LVE.energy_erased",
    "local_community_1.energy_bought_outside", "local_community_2.energy_bought_outside",
    "local_community_1.energy_sold_outside", "local_community_2.energy_sold_outside"
]  # métriques utilisées au moment de la définition des clusters, spécifiques au cas étudié...

performance_metrics = [
    "residential_dwellings.LVE.energy_erased", "industrial_process.LVE.energy_erased",
    "local_community_1.energy_bought_outside", "local_community_2.energy_bought_outside",
    "local_community_1.energy_sold_outside", "local_community_2.energy_sold_outside",
    "unwanted_delivery_cuts"
]  # critères de performance, spécifiques au cas étudié...


exported_metrics = performance_metrics + clustering_metrics

coef = 1
def performance_norm(performance_vector: Dict) -> float:
    return (abs(sum(performance_vector["local_community_1.energy_sold_outside"]))
            + abs(sum(performance_vector["local_community_2.energy_sold_outside"]))
            - abs(sum(performance_vector["local_community_1.energy_bought_outside"]))
            - abs(sum(performance_vector["local_community_2.energy_bought_outside"]))
            - abs(sum(performance_vector["residential_dwellings.LVE.energy_erased"]))
            - abs(sum(performance_vector["industrial_process.LVE.energy_erased"]))
            - sum(performance_vector["unwanted_delivery_cuts"]) * 10)  # non respect of the minimum constraints

# ######################################################################################################################
# strategies, defined as an ordered list of the available levers
# ######################################################################################################################

consumption_options_1 = ["residential", "nothing", "storage", "sellGrid"]
consumption_options_2 = ["industrial", "nothing", "sellGrid"]
production_options_1 = ["Diesel_generator", "unstorage", "buyGrid"]
production_options_2 = ["Step", "buyGrid"]
assessed_priorities_consumption_1 = [list(toto) for toto in itertools.permutations(consumption_options_1)]
assessed_priorities_consumption_2 = [list(toto) for toto in itertools.permutations(consumption_options_2)]
assessed_priorities_production_1 = [list(toto) for toto in itertools.permutations(production_options_1)]
assessed_priorities_production_2 = [list(toto) for toto in itertools.permutations(production_options_2)]
assessed_priorities_1 = {"consumption": assessed_priorities_consumption_1, "production": assessed_priorities_production_1}
assessed_priorities_2 = {"consumption": assessed_priorities_consumption_2, "production": assessed_priorities_production_2}


# reference strategies
def ref_priorities_consumption_1(strategy: "Strategy"):
    electricity_consumption = strategy._catalog.get("residential_dwellings.LVE.energy_wanted")["energy_maximum"]
    pv_production = strategy._catalog.get("PV_field_1.LVE.energy_wanted")["energy_maximum"]
    wt_production = strategy._catalog.get("WT_field_1.LVE.energy_wanted")["energy_maximum"]
    dg_production = strategy._catalog.get("Diesel_generator.LVE.energy_wanted")["energy_maximum"]

    if abs(electricity_consumption) >= abs(pv_production) + abs(wt_production) + abs(dg_production):
        return ["residential", "nothing", "storage", "sellGrid"]
    else:
        return ["residential", "storage", "sellGrid", "nothing"]


def ref_priorities_consumption_2(strategy: "Strategy"):
    electricity_consumption = strategy._catalog.get("industrial_process.LVE.energy_wanted")["energy_maximum"]
    electricity_production = strategy._catalog.get("Step.LVE.energy_wanted")["energy_maximum"]

    if abs(electricity_consumption) >= abs(electricity_production):
        return ["industrial", "nothing", "sellGrid"]
    else:
        return ["industrial", "sellGrid", "nothing"]


def ref_priorities_production_1(strategy: "Strategy"):
    return ["Diesel_generator", "unstorage", "buyGrid"]


def ref_priorities_production_2(strategy: "Strategy"):
    return ["Step", "buyGrid"]