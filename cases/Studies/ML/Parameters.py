from random import seed


from cases.Studies.ML.Utilities import *

# ######################################################################################################################
#
# ######################################################################################################################
training_simulation_length = 24  # length of sequences used for clustering.


cluster_number = 10  # the number of clusters, fixed arbitrarily, can be determined studying the dispersion inside each cluster (see elbow method)


random_seed = "tournesol"  # random seed is set to have always the same result for 1 given set of parameters
seed(random_seed)


comparison_simulation_length = 8760  # length of the final run aimed at evaluating the efficiency of the strategy


# ######################################################################################################################
# metrics
# ######################################################################################################################
clustering_metrics = [  # prices are not taken into account for now
    # meteo ?
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
]  # critères de performance, spécifiques au cas étudié...


def performance_norm(performance_vector: Dict)-> float: # on peut bien évidemment prendre une norme plus complexe
    return sum(performance_vector["general_aggregator.coverage_rate"])


# ######################################################################################################################
# strategies, defined as an ordered list of the available levers
# ######################################################################################################################
tested_strategies = {
    "toto": {"consumption": random_order_priorities_conso(), "production": random_order_priorities_prod()},
    "tutu": {"consumption": random_order_priorities_conso(), "production": random_order_priorities_prod()},
    "titi": {"consumption": random_order_priorities_conso(), "production": random_order_priorities_prod()},
    }  # Ici on teste un set prédéfini de stratégies
# vrai problème de définition de l'espace des stratégies (espace évolutif, type recherche heuristique ? coûteux mais devrait fonctionner et moins coûteux qu'un test systématique)


# reference strategies
# exchange first, then storage and DSM if nothing else
def ref_priorities_consumption(strategy: "Strategy"):
    return ['buy_outside_emergency', 'store', 'soft_DSM_conso', 'hard_DSM_conso',]


def ref_priorities_production(strategy: "Strategy"):
    return ['sell_outside_emergency', 'unstore', 'soft_DSM_prod', 'hard_DSM_prod',]

