from cases.Studies.ML.Utilities import *
from cases.Studies.ML.CasesStudied.Test.SimulationScript import create_simulation

import math
from numpy import zeros, mean
from typing import List
from sklearn import cluster
# lien pour les fonctions de clustering https://scikit-learn.org/stable/auto_examples/cluster/plot_cluster_comparison.html


def clustering(simulation_length: int, clusters_number: int, clustering_metrics: List, days_number: int, sequences_gap: int):
    delay_days = [sequences_gap * i for i in range(days_number)]

    print(f"creation of the situation set")
    raw_situations = {key: [] for key in clustering_metrics}
    for day in delay_days:
        print(f"situation starting at day {day}")
        metrics_datalogger = create_simulation(simulation_length, random_order_priorities_conso(),
                                               random_order_priorities_prod(), f"clustering/sequence_{day}",
                                               clustering_metrics, delay_days=day)
        # récuérer moyennes pour normaliser métriques
        for key in clustering_metrics:
            raw_situations[key] = raw_situations[key] + metrics_datalogger._values[key]
    print("Done\n")

    print(f"construction of the description of the situations")
    refined_situations = zeros((len(delay_days), len(clustering_metrics)))
    normalisation_values = []
    j = 0
    for key, recorded_values in raw_situations.items():
        key_mean = mean(recorded_values)
        for i in range(len(delay_days)):
            refined_situations[i][j] = recorded_values[i]/key_mean
        j += 1
    print("Done\n")

    print(f"identification of clusters")
    clusters = cluster.KMeans(clusters_number).fit(refined_situations)
    situations_list = [[] for _ in range(len(raw_situations[0]))]
    for criterion in raw_situations:
        i = 0
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
