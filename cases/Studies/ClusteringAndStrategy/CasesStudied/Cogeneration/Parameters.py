from random import seed
import numpy as np
import itertools


from cases.Studies.ClusteringAndStrategy.Utilities import *

# ######################################################################################################################
# hyperparameters -
# ######################################################################################################################
training_simulation_length = 8760  # length of sequences used for training
comparison_simulation_length = 8760  # length of the final run aimed at evaluating the efficiency of the strategy
clustering_batch_size = 3  # number of years simulated for clustering
cluster_number = 5  # number of clusters wanted for clustering

# ######################################################################################################################
# metrics
# ######################################################################################################################
clustering_metrics = [  # prices are not taken into account for now
    # consumption
    "district_heating_microgrid.minimum_energy_consumption",
    # production
    "district_heating_microgrid.maximum_energy_production",
]  # métriques utilisées au moment de la définition des clusters, spécifiques au cas étudié...

performance_metrics = [
    "CHP_unit.LTH.energy_sold",
    "CHP_unit.LVE.energy_sold",
    "CHP_unit.LPG.energy_bought",
    "HP_unit.LTH.energy_sold",
    "HP_unit.LVE.energy_bought",
    "unwanted_delivery_cuts",
]  # critères de performance, spécifiques au cas étudié...


exported_metrics = performance_metrics + clustering_metrics + [
    "district_heating_microgrid.energy_bought_outside",

]


coef = 3
def performance_norm(performance_vector: Dict) -> float:
    performance = sum(performance_vector["biomass_plant.LTH.energy_sold"]) - sum(performance_vector["heat_sink.LTH.energy_bought"]) * coef\
                  - sum(performance_vector["unwanted_delivery_cuts"]) * 10  # non respect of the minimum constraints
    return performance

# ######################################################################################################################
# strategies, defined as an ordered list of the available levers
# ######################################################################################################################
consumption_options = ["dissipation", "nothing"]
production_options = ["biomass", "gas", "nothing"]
assessed_priorities_consumption = [list(toto) for toto in itertools.permutations(consumption_options)]
assessed_priorities_production = [list(toto) for toto in itertools.permutations(production_options)]
assessed_priorities = {"consumption": assessed_priorities_consumption, "production": assessed_priorities_production}

threshold = 0.85
# reference strategies
def ref_priorities_consumption(strategy: "Strategy"):
    real_consumption = strategy._catalog.get("old_house.LTH.energy_wanted")["energy_maximum"]
    biomass_previous_power = strategy._catalog.get("dictionaries")['devices']['biomass_plant'].last_energy
    current_time = strategy._catalog.get("simulation_time")


def ref_priorities_production(strategy: "Strategy"):
    real_consumption = strategy._catalog.get("")["energy_maximum"]
    biomass_previous_power = strategy._catalog.get("dictionaries")['devices']['biomass_plant'].last_energy
    current_time = strategy._catalog.get("simulation_time")
