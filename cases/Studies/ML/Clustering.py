import gc

from cases.Studies.ML.Utilities import *
from cases.Studies.ML.SimulationScript import create_simulation

import math
from numpy import average, std, zeros
from typing import List
from sklearn import cluster
# lien pour les fonctions de clustering https://scikit-learn.org/stable/auto_examples/cluster/plot_cluster_comparison.html


def clustering(simulation_length: int, clusters_number: int, clustering_metrics: List, days_number: int, sequences_gap: int):
    delay_days = [i for i in range(days_number)]

    print(f"creation of the situation set")
    raw_situations = {key: [] for key in clustering_metrics}
    for day in delay_days:
        print(f"situation starting at day {day}")
        metrics_datalogger = create_simulation(simulation_length, random_order_priorities_conso(),
                                               random_order_priorities_prod(), f"clustering/sequence_{day}", clustering_metrics, delay_days=day)
        for key in clustering_metrics:
            raw_situations[key] = raw_situations[key] + metrics_datalogger._values[key]
    print("Done\n")

    # # approche centrage et réduction sur chaque variable, probablement pas bonne du lien entre variables
    # refined_situations = {key: [] for key in metrics}
    # for key in metrics:
    #     mean = average(raw_situations[key])
    #     maximum = max(raw_situations[key])
    #     minimum = min(raw_situations[key])
    #     refined_situations[key] = [(value - mean)/(maximum - minimum) for value in raw_situations[key]]
    #     # print(f"{key}: {refined_situations[key]}")
    #     # print(std(refined_situations[key]))

    # approche centrage par rapport au minimum d'energie demandée en consommation
    # qui de fait disparaît des métriques
    print(f"construction of the description of the situations")
    refined_situations = zeros((len(delay_days), len(clustering_metrics)-1))
    normalisation_values = []
    for i in range(len(delay_days)):
        min_cons = raw_situations["general_aggregator.minimum_energy_consumption"][i]
        normalisation_values.append(min_cons)
        refined_situations[i][0] = raw_situations["battery.energy_stored"][i] / min_cons  # energy stored

        refined_situations[i][1] = raw_situations["general_aggregator.maximum_energy_consumption"][i] / min_cons  # max consumption

        refined_situations[i][2] = raw_situations["general_aggregator.minimum_energy_production"][i] / min_cons  # min production
        refined_situations[i][3] = raw_situations["general_aggregator.maximum_energy_production"][i] / min_cons  # max production
    print("Done\n")

    print(f"identification of clusters")
    clusters = cluster.KMeans(clusters_number).fit(refined_situations)
    situations_list = [[] for _ in range(len(raw_situations["battery.energy_stored"]))]
    for criterion in raw_situations:
        i = 0
        if criterion != "general_aggregator.minimum_energy_consumption":
            for value in raw_situations[criterion]:
                situations_list[i].append(value)
                i += 1

    cluster_centers = []
    for i in range(len(clusters.cluster_centers_)):
        refined_center = clusters.cluster_centers_[i]
        raw_center = refined_center * normalisation_values[i]
        cluster_centers.append(list(raw_center))

    # retrouver le jour le plus proche de chaque centre
    cluster_days = []
    for center in cluster_centers:
        indice = 0
        distance_min = math.inf
        for i in range(len(delay_days)):
            situation = situations_list[i]
            distance = sum([(center[j] - situation[j])**2 for j in range(len(center))])
            if distance < distance_min:
                distance_min = distance
                indice = i
        cluster_days.append(indice)
    print("Done\n")

    print(f"cluster centers: {cluster_centers}")
    print(f"cluster days: {cluster_days}")
    print("\n\n")

    return cluster_centers, cluster_days
