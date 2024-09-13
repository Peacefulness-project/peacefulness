from cases.Studies.ClusteringAndStrategy.Utilities import *

import math
from numpy import zeros, mean
from typing import List
from sklearn import cluster
# lien pour les fonctions de clustering https://scikit-learn.org/stable/auto_examples/cluster/plot_cluster_comparison.html


def clustering(simulation_length: int, clusters_number: int, clustering_metrics: List, sequences_number: int, sequences_gap: int, create_simulation: Callable, consumption_options: List, production_options: List):
    delay = [sequences_gap * i for i in range(sequences_number)]

    print(f"creation of the situation set")
    raw_situations = {key: [] for key in clustering_metrics}
    for start_point in delay:
        print(f"situation starting {start_point} hours past the initial start")
        metrics_datalogger = create_simulation(simulation_length, random_order_priorities(consumption_options),
                                               random_order_priorities(production_options), f"clustering/sequence_{start_point}",
                                               clustering_metrics, delay_days=start_point)
        # récupérer moyennes pour normaliser métriques
        for key in clustering_metrics:
            raw_situations[key] = raw_situations[key] + metrics_datalogger._values[key]
    print("Done\n")

    print(f"construction of the description of the situations")
    refined_situations = zeros((len(delay), len(clustering_metrics)))
    normalisation_values = []
    j = 0
    for key, recorded_values in raw_situations.items():
        key_mean = mean(recorded_values)
        normalisation_values.append(key_mean)
        for i in range(len(delay)):
            refined_situations[i][j] = recorded_values[i]/key_mean
        j += 1
    print("Done\n")

    print(f"identification of clusters")
    clusters = cluster.KMeans(clusters_number).fit(refined_situations)
    situations_list = [[] for _ in range(len(raw_situations[key]))]
    for criterion in raw_situations:
        i = 0
        for value in raw_situations[criterion]:
            situations_list[i].append(value)
            i += 1

    cluster_centers = []
    for i in range(len(clusters.cluster_centers_)):
        refined_center = clusters.cluster_centers_[i]
        raw_center = [refined_center[j] * normalisation_values[j] for j in range(len(normalisation_values))]
        cluster_centers.append(list(raw_center))

    # retrouver le jour le plus proche de chaque centre
    cluster_days = []
    for center in cluster_centers:
        indice = 0
        distance_min = math.inf
        for i in range(len(delay)):
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
