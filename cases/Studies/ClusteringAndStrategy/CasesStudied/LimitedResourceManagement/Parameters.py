import itertools


from cases.Studies.ClusteringAndStrategy.Utilities import *

# ######################################################################################################################
#
# ######################################################################################################################
training_simulation_length = 8760  # length of sequences used for clustering.
clustering_sequences_number = 2  # number of sequences simulated
gap = 1  # gap (given in iterations) between 2 sequences simulated


comparison_simulation_length = 8760  # length of the final run aimed at evaluating the efficiency of the strategy


# ######################################################################################################################
# metrics
# ######################################################################################################################
clustering_metrics = [  # prices are not taken into account for now
    # storage
    "storage.energy_stored",
    # consumption
    "local_network.minimum_energy_consumption",
    "local_network.maximum_energy_consumption",
]  # métriques utilisées au moment de la définition des clusters, spécifiques au cas étudié...

performance_metrics = [
    "local_network.energy_bought_outside",
    "unwanted_delivery_cuts",
    "industrial_process.LVE.energy_bought",
]  # critères de performance, spécifiques au cas étudié...

exported_metrics = performance_metrics + clustering_metrics + [
    "storage.LVE.energy_bought",
    "storage.LVE.energy_sold",
    "residential_dwellings.LVE.energy_bought",
    "production.LVE.energy_sold"
]

coef = 0.5
def performance_norm(performance_vector: Dict) -> float:  # on peut bien évidemment prendre une norme plus complexe
    return - sum(performance_vector["local_network.energy_bought_outside"]) + sum(performance_vector["industrial_process.LVE.energy_bought"]) * coef\
           - sum(performance_vector["unwanted_delivery_cuts"]) * 10  # non respect of the minimum constraints


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
    current_situation = {}
    current_situation["residential_dwellings.demand"] = strategy._catalog.get("residential_dwellings.LVE.energy_wanted")["energy_maximum"]
    current_situation["industrial_process.demand"] = strategy._catalog.get("industrial_process.LVE.energy_wanted")["energy_maximum"]
    current_situation["industrial_process.demand_min"] = strategy._catalog.get("industrial_process.LVE.energy_wanted")["energy_minimum"]
    minimum_consumption = current_situation["residential_dwellings.demand"] + current_situation["industrial_process.demand_min"]
    total_consumption = current_situation["residential_dwellings.demand"] + \
                        current_situation["industrial_process.demand"]
    max_prod = 175  # TODO: à paramétrer parce qu'en l'état c'est dégueu...
    unstorage = - strategy._catalog.get("storage.LVE.energy_wanted")["energy_minimum"]
    if current_situation["residential_dwellings.demand"] > max_prod + unstorage:  # if minimal consumption is superior to the production...
        return ["nothing", "industrial", "storage"]  # ...industrials are cut if possible
    elif total_consumption > max_prod:
        return ["industrial", "nothing", "storage"]  # ... no storage is done
    else:
        return ["industrial", "storage", "nothing"]  # ... storage is done


def ref_priorities_production(strategy: "Strategy"):
    return ["production", "unstorage", "grid"]

