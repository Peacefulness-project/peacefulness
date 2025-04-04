from random import seed
import numpy as np
import itertools


from cases.Studies.ClusteringAndStrategy.Utilities import *

# ######################################################################################################################
# hyperparameters -
# ######################################################################################################################
training_simulation_length = 8760  # length of sequences used for clustering.
clustering_sequences_number = 2  # number of sequences simulated
gap = 1  # gap (given in iterations) between 2 sequences simulated


comparison_simulation_length = 8760  # length of the final run aimed at evaluating the efficiency of the strategy


# ######################################################################################################################
# metrics
# ######################################################################################################################
clustering_metrics = [  # prices are not taken into account for now
    "home_aggregator.energy_bought_outside",
    "home_aggregator.energy_sold_outside"
]  # métriques utilisées au moment de la définition des clusters, spécifiques au cas étudié...

performance_metrics = [
    "home_aggregator.energy_bought_outside",
    "home_aggregator.energy_sold_outside",
    "unwanted_delivery_cuts"
]  # critères de performance, spécifiques au cas étudié...


exported_metrics = performance_metrics + clustering_metrics

coef = 1
def performance_norm(performance_vector: Dict) -> float:
    return abs(sum(performance_vector["home_aggregator.energy_sold_outside"])) - abs(sum(performance_vector["home_aggregator.energy_bought_outside"])) * coef\
           - sum(performance_vector["unwanted_delivery_cuts"]) * 10  # non respect of the minimum constraints

# ######################################################################################################################
# strategies, defined as an ordered list of the available levers
# ######################################################################################################################

consumption_options = ["storage", "nothing"]
production_options = ["production", "unstorage", "grid"]
assessed_priorities_consumption = [list(toto) for toto in itertools.permutations(consumption_options)]
assessed_priorities_production = [list(toto) for toto in itertools.permutations(production_options)]
assessed_priorities = {"consumption": assessed_priorities_consumption, "production": assessed_priorities_production}

# reference strategies
def ref_priorities_consumption(strategy: "Strategy"):
    return ["storage", "nothing"]


def ref_priorities_production(strategy: "Strategy"):
    return ["production", "unstorage", "grid"]