from random import seed
import itertools


from cases.Studies.ClusteringAndStrategy.Utilities import *

# ######################################################################################################################
# hyperparameters
# ######################################################################################################################
training_simulation_length = 8760  # length of sequences used for clustering.
sequences_number = 8760  # number of sequences simulated
clustering_batch_size = 4  # number of years simulated for clustering
cluster_number = 10  # the number of clusters, fixed arbitrarily, can be determined studying the dispersion inside each cluster (see elbow method)

# random_seed = "tournesol"  # random seed is set to have always the same result for 1 given set of parameters
# seed(random_seed)


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
    "heat_pump.LVE.energy_bought",
    "heat_pump.LTH.energy_sold",

    "heat_storage.LTH.energy_bought",
    "heat_storage.LTH.energy_sold",
    "unwanted_delivery_cuts",
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
def ref_priorities_consumption(strategy: "Strategy"):
    efficiency = strategy._catalog.get("heat_pump.LTH.efficiency")
    prod_PV = strategy._catalog.get("PV.LVE.energy_wanted")["energy_maximum"]
    local_heat_pump = - efficiency * prod_PV
    heat_need = strategy._catalog.get("heating.LTH.energy_wanted")["energy_maximum"]

    if local_heat_pump > heat_need:
        return ["spatial_heating", "long_term_storage", "nothing", ]
    else:
        return ["spatial_heating", "nothing", "long_term_storage", ]


def ref_priorities_production(strategy: "Strategy"):
    return ["long_term_unstorage", "heat_pump", ]


