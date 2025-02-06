from random import seed
import numpy as np
import itertools


from cases.Studies.ClusteringAndStrategy.Utilities import *

# ######################################################################################################################
#
# ######################################################################################################################
training_simulation_length = 1  # length of sequences used for clustering.
sequences_number = 8760  # number of sequences simulated
gap = 1  # gap (given in iterations) between 2 sequences simulated
cluster_number = 30  # the number of clusters, fixed arbitrarily, can be determined studying the dispersion inside each cluster (see elbow method)


random_seed = "tournesol"  # random seed is set to have always the same result for 1 given set of parameters
seed(random_seed)


comparison_simulation_length = 8760  # length of the final run aimed at evaluating the efficiency of the strategy


# ######################################################################################################################
# metrics
# ######################################################################################################################
clustering_metrics = [  # prices are not taken into account for now
    # storage
    "storage.energy_stored",
    # consumption
    "_representative_dwelling_0.LVE.energy_bought",
    "industrial_consumer.LVE.energy_bought",
    # + demande en attente ?
]  # métriques utilisées au moment de la définition des clusters, spécifiques au cas étudié...

performance_metrics = [
    "local_network.coverage_rate",
    # "local_network.LVE.energy_bought_outside",
]  # critères de performance, spécifiques au cas étudié...


def performance_norm(performance_vector: Dict) -> float:  # on peut bien évidemment prendre une norme plus complexe
    return -sum(performance_vector["local_network.coverage_rate"])


# ######################################################################################################################
# strategies, defined as an ordered list of the available levers
# ######################################################################################################################

consumption_options = ["storage", "nothing", "industrial"]
production_options = ["production", "unstorage", "grid"]
assessed_priorities_consumption = [list(toto) for toto in itertools.permutations(consumption_options)]
assessed_priorities_production = [list(toto) for toto in itertools.permutations(production_options)]
assessed_priorities = {"consumption": assessed_priorities_consumption, "production": assessed_priorities_production}


# reference strategies
# exchange first, then storage and DSM if nothing else
def ref_priorities_consumption(strategy: "Strategy"):
    return ["storage", "nothing", "industrial"]


def ref_priorities_production(strategy: "Strategy"):
    return ["production", "unstorage", "grid"]


