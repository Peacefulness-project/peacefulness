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
    "heat_storage.energy_stored",
    # consumption
    "heating.LTH.energy_bought",
    "prices_elec.France.buying_price",
    # production
    "PV.LVE.energy_sold",
    "heat_pump.LTH.efficiency",
    # + demande en attente ?
]  # métriques utilisées au moment de la définition des clusters, spécifiques au cas étudié...

performance_metrics = [
    "house_owner.money_earned",
    "house_owner.money_spent",
    "heat_storage.LTH.energy_bought",
    "heat_storage.LTH.energy_sold",
]  # critères de performance, spécifiques au cas étudié...

money_coef = 1*0  # money costs around 10 C€/kWh and energy flows are around 1-10 kWH
storage_coef = 1/10  # same reflexion on 1-10kWh


def performance_norm(performance_vector: Dict) -> float:  # on peut bien évidemment prendre une norme plus complexe
    print(sum(performance_vector["heat_storage.LTH.energy_bought"]))
    return (sum(performance_vector["house_owner.money_spent"]) - sum(performance_vector["house_owner.money_earned"])) * money_coef + \
           (sum(performance_vector["heat_storage.LTH.energy_sold"]) - sum(performance_vector["heat_storage.LTH.energy_bought"])) * storage_coef


# ######################################################################################################################
# strategies, defined as an ordered list of the available levers
# ######################################################################################################################

consumption_options = ["spatial_heating", "long_term_storage", "nothing"]
production_options = ["long_term_unstorage", "heat_pump", ]
assessed_priorities_consumption = [list(toto) for toto in itertools.permutations(consumption_options)]
assessed_priorities_production = [list(toto) for toto in itertools.permutations(production_options)]
assessed_priorities = {"consumption": assessed_priorities_consumption, "production": assessed_priorities_production}


# reference strategies
# exchange first, then storage and DSM if nothing else
def ref_priorities_consumption(strategy: "Strategy"):
    return ["spatial_heating", "long_term_storage", "nothing", ]


def ref_priorities_production(strategy: "Strategy"):
    return ["heat_pump", "long_term_unstorage"]


