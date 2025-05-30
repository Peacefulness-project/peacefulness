from random import seed
import numpy as np
import itertools


from cases.Studies.ClusteringAndStrategy.Utilities import *

# ######################################################################################################################
#
# ######################################################################################################################
training_simulation_length = 3  # length of sequences used for clustering.
days_number = 20  # number of sequences simulated
gap = 6  # gap (given in iterations) between 2 sequences simulated

cluster_number = 3  # the number of clusters, fixed arbitrarily, can be determined studying the dispersion inside each cluster (see elbow method)


random_seed = "tournesol"  # random seed is set to have always the same result for 1 given set of parameters
seed(random_seed)


comparison_simulation_length = 8760 // 24  # length of the final run aimed at evaluating the efficiency of the strategy


# ######################################################################################################################
# metrics
# ######################################################################################################################
clustering_metrics = [  # prices are not taken into account for now
    # storage
    "battery.energy_stored",
    # consumption
    "general_aggregator.minimum_energy_consumption",
    "general_aggregator.maximum_energy_consumption",
    # production
    "general_aggregator.minimum_energy_production",
    "general_aggregator.maximum_energy_production",
    # + demande en attente ?
]  # métriques utilisées au moment de la définition des clusters, spécifiques au cas étudié...

performance_metrics = [
    "general_aggregator.coverage_rate",
    "general_aggregator.self_consumption",
    "general_aggregator.curtailment_rate_consumption",
]  # critères de performance, spécifiques au cas étudié...


def performance_norm(performance_vector: Dict) -> float:  # on peut bien évidemment prendre une norme plus complexe
    return np.mean(performance_vector["general_aggregator.coverage_rate"]) + np.mean(performance_vector["general_aggregator.self_consumption"]) \
           - 2 * np.mean(performance_vector["general_aggregator.curtailment_rate_consumption"])


# ######################################################################################################################
# strategies, defined as an ordered list of the available levers
# ######################################################################################################################

consumption_options = ['store', 'soft_DSM_conso', 'buy_outside_emergency', 'hard_DSM_conso']
production_options = ['unstore', 'soft_DSM_prod', 'sell_outside_emergency', 'hard_DSM_prod']
assessed_priorities_consumption = [list(toto) for toto in itertools.permutations(consumption_options)]
assessed_priorities_production = [list(toto) for toto in itertools.permutations(production_options)]
assessed_priorities = {"consumption": assessed_priorities_consumption, "production": assessed_priorities_production}


# reference strategies
# exchange first, then storage and DSM if nothing else
def ref_priorities_consumption(strategy: "Strategy"):
    return ['store', 'soft_DSM_conso', 'buy_outside_emergency', 'hard_DSM_conso', ]


def ref_priorities_production(strategy: "Strategy"):
    return ['unstore', 'soft_DSM_prod', 'sell_outside_emergency', 'hard_DSM_prod', ]

