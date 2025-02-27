from random import seed
import itertools


from cases.Studies.ClusteringAndStrategy.Utilities import *

# ######################################################################################################################
# hyperparameters
# ######################################################################################################################
training_simulation_length = 8760  # length of sequences used for clustering.
sequences_number = 8760  # number of sequences simulated
gap = 1  # gap (given in iterations) between 2 sequences simulated
cluster_number = 5  # the number of clusters, fixed arbitrarily, can be determined studying the dispersion inside each cluster (see elbow method)


random_seed = "tournesol"  # random seed is set to have always the same result for 1 given set of parameters
seed(random_seed)


comparison_simulation_length = 8760  # length of the final run aimed at evaluating the efficiency of the strategy


# ######################################################################################################################
# metrics
# ######################################################################################################################
clustering_metrics = [  # prices are not taken into account for now
    # storage
    "heat_storage.energy_stored",
    # consumption
    "heating.LTH.energy_bought",
    "prices_elec.France.buying_price",
    # production
    "PV.LVE.energy_sold",
    # "heat_pump.LTH.efficiency",
    # + demande en attente ?
]  # métriques utilisées au moment de la définition des clusters, spécifiques au cas étudié...

performance_metrics = [
    "house_owner.money_earned",
    "house_owner.money_spent",

    "heat_storage.LTH.energy_bought",
    "heat_storage.LTH.energy_sold",
    "unwanted_delivery_cuts",

    # "heat_pump.LVE.energy_bought",
    # "heat_pump.LTH.energy_sold",
    #
    # "heating.LTH.energy_bought",
    # "heating.LTH.energy_sold",
    #
    # "house_owner.LTH.energy_bought",
    # "house_owner.LTH.energy_sold",
    # "house_owner.LVE.energy_sold",
    # "house_owner.LVE.energy_bought",
    #
    # "PV.LVE.energy_sold",
    #
    # "house_elec.energy_sold",
    # "house_elec.energy_bought",
]  # critères de performance, spécifiques au cas étudié...

exported_metrics = performance_metrics + clustering_metrics


def performance_norm(performance_vector: Dict) -> float:
    return sum(performance_vector["house_owner.money_spent"]) - sum(performance_vector["house_owner.money_earned"]) - \
           sum(performance_vector["unwanted_delivery_cuts"]) * 10  # non respect of the minimum constraints


# ######################################################################################################################
# strategies, defined as an ordered list of the available levers
# ######################################################################################################################

consumption_options = ["spatial_heating", "long_term_storage", "nothing", ]
production_options = ["long_term_unstorage", "heat_pump", ]
assessed_priorities_consumption = [list(toto) for toto in itertools.permutations(consumption_options)]
assessed_priorities_production = [list(toto) for toto in itertools.permutations(production_options)]
assessed_priorities = {"consumption": assessed_priorities_consumption, "production": assessed_priorities_production}


# reference strategies
# exchange first, then storage and DSM if nothing else
def ref_priorities_consumption(strategy: "Strategy"):
    return ["spatial_heating", "long_term_storage", "nothing", ]


def ref_priorities_production(strategy: "Strategy"):
    return ["heat_pump", "long_term_unstorage", ]


