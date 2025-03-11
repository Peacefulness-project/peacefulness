import copy

from cases.Studies.ClusteringAndStrategy.Utilities import *

import math
from numpy import zeros, mean
from typing import List
from sklearn import cluster
# lien pour les fonctions de clustering https://scikit-learn.org/stable/auto_examples/cluster/plot_cluster_comparison.html


def situations_recording(clustering_metrics: List, sequences_number: int, create_simulation: Callable, consumption_options: List, production_options: List, complement_path: str):
    print(f"creation of the situation set")
    raw_situations = {key: [] for key in clustering_metrics}
    for i in range(sequences_number):
            print(f"situation starting {i} hours past the initial start")
            metrics_datalogger = create_simulation(8760, random_order_priorities(consumption_options),
                                                   random_order_priorities(production_options), f"{complement_path}/clustering/sequence_{i}",
                                                   clustering_metrics, delay_days=i, random_seed=f"{i}_seed", standard_deviation=0.1)
            # récupérer moyennes pour normaliser métriques
            for key in clustering_metrics:
                raw_situations[key] = raw_situations[key] + metrics_datalogger._values[key]
    print("Done\n")

    return raw_situations


def clustering(clusters_number: int, clustering_metrics: List, raw_situations, sequences_number: int):
    print(f"construction of the description of the situations")
    sequences_number *= 8760
    refined_situations = zeros((sequences_number, len(clustering_metrics)))
    normalisation_values = []
    j = 0
    new_raw_situations = zeros((sequences_number, len(clustering_metrics)))
    for key, recorded_values in raw_situations.items():
        key_mean = mean(recorded_values)
        normalisation_values.append(key_mean)
        for i in range(sequences_number):
            refined_situations[i][j] = recorded_values[i]/key_mean
            new_raw_situations[i][j] = recorded_values[i]
        j += 1
    print("Done\n")

    print(f"identification of clusters")
    print(refined_situations)
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
        for i in range(sequences_number):
            situation = situations_list[i]
            distance = sum([(center[j] - situation[j])**2 for j in range(len(center))])
            if distance < distance_min:
                distance_min = distance
                indice = i
        cluster_days.append(indice)
    print("Done\n")

    # ordonner les cluster dans l'ordre croissant du nombre de séquences qui y sont incluses
    print("sorting of cluster by size")
    # number of sequences by cluster
    sequences_count = [0 for i in range(clusters_number)]
    for sequence in new_raw_situations:
        distance_min = math.inf
        for i in range(len(cluster_centers)):
            center = cluster_centers[i]
            distance = sum([(center[j] - sequence[j]) ** 2 for j in range(len(center))])
            if distance < distance_min:
                distance_min = distance
                cluster_id = i
        sequences_count[cluster_id] += 1
    # sorting of clusters
    cluster_rank = [0 for i in range(clusters_number)]
    for i in range(clusters_number):
        count = 0
        for j in range(clusters_number):
            if sequences_count[j] < sequences_count[i]:
                count += 1
        cluster_rank[count] = i
    sorted_cluster_centers = [cluster_centers[i] for i in cluster_rank]
    sorted_cluster_days = [cluster_days[i] for i in cluster_rank]
    sequences_count = sorted(sequences_count)
    print("Done\n")

    print(f"cluster centers: {cluster_centers}")
    print(f"cluster days: {cluster_days}")
    print("\n\n")
    return sorted_cluster_centers, sorted_cluster_days, sequences_count
