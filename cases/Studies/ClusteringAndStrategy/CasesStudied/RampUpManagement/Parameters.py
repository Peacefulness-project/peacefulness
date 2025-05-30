from random import seed
import numpy as np
import itertools


from cases.Studies.ClusteringAndStrategy.Utilities import *

# ######################################################################################################################
# hyperparameters -
# ######################################################################################################################
training_simulation_length = 8760  # length of sequences used for training
comparison_simulation_length = 8760  # length of the final run aimed at evaluating the efficiency of the strategy
clustering_batch_size = 2  # number of years simulated for clustering
cluster_number = 3  # number of clusters wanted for clustering

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
    "biomass_plant.LTH.energy_sold",
    "heat_sink.LTH.energy_bought",
    "unwanted_delivery_cuts",
]  # critères de performance, spécifiques au cas étudié...


exported_metrics = performance_metrics + clustering_metrics + [
    "district_heating_microgrid.energy_bought_outside",
    "LTH.energy_consumed",
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
    real_consumption = 0.0
    real_consumption += strategy._catalog.get("old_house.LTH.energy_wanted")["energy_maximum"]
    real_consumption += strategy._catalog.get("new_house.LTH.energy_wanted")["energy_maximum"]
    real_consumption += strategy._catalog.get("office.LTH.energy_wanted")["energy_maximum"]
    biomass_previous_power = strategy._catalog.get("dictionaries")['devices']['biomass_plant'].last_energy
    current_time = strategy._catalog.get("simulation_time")

    if real_consumption > abs(biomass_previous_power):
        return ["nothing", "dissipation"]
    else:
        if current_time < 2712:  # for the first heating season
            if current_time % 24 > 9:
                return ["nothing", "dissipation"]
            else:
                if real_consumption >= threshold * abs(biomass_previous_power):  # threshold for accepting dissipation
                    return ["dissipation", "nothing"]
                else:  # if the consumption per generation ratio is less than the threshold we decrease generation power
                    return ["nothing", "dissipation"]
        elif current_time >= 6144:  # for the second heating season
            if 9 < current_time % 24 < 17:  # middle of the day
                return ["nothing", "dissipation"]
            else:  # from midnight to 8 and from 17 to midnight
                if real_consumption >= threshold * abs(biomass_previous_power):  # threshold for accepting dissipation
                    return ["dissipation", "nothing"]
                else:  # if the consumption per generation ratio is less than the threshold we decrease generation power
                    return ["nothing", "dissipation"]
        else:  # the rest of the year
            return ["nothing", "dissipation"]


def ref_priorities_production(strategy: "Strategy"):
    real_consumption = 0.0
    real_consumption += strategy._catalog.get("old_house.LTH.energy_wanted")["energy_maximum"]
    real_consumption += strategy._catalog.get("new_house.LTH.energy_wanted")["energy_maximum"]
    real_consumption += strategy._catalog.get("office.LTH.energy_wanted")["energy_maximum"]
    biomass_previous_power = strategy._catalog.get("dictionaries")['devices']['biomass_plant'].last_energy
    current_time = strategy._catalog.get("simulation_time")
    if real_consumption > abs(biomass_previous_power):
        return ["biomass", "gas", "nothing"]
    else:
        if current_time < 2712:  # for the first heating season
            if current_time % 24 > 9:
                return ["biomass", "gas", "nothing"]
            else:
                if real_consumption >= threshold * abs(biomass_previous_power):  # threshold for accepting dissipation
                    return ["biomass", "nothing", "gas"]
                else:  # if the consumption per generation ratio is less than the threshold we decrease generation power
                    return ["biomass", "gas", "nothing"]
        elif current_time >= 6144:  # for the second heating season
            if 9 < current_time % 24 < 17:  # middle of the day
                return ["biomass", "gas", "nothing"]
            else:  # from midnight to 8 and from 17 to midnight
                if real_consumption >= threshold * abs(biomass_previous_power):  # threshold for accepting dissipation
                    return ["biomass", "nothing", "gas"]
                else:  # if the consumption per generation ratio is less than the threshold we decrease generation power
                    return ["biomass", "gas", "nothing"]
        else:  # the rest of the year
            return ["nothing", "biomass", "gas"]
