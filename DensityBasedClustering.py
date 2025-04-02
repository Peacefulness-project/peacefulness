import copy

from cases.Studies.ClusteringAndStrategy.Utilities import *

import math
import numpy as np
from typing import List
from sklearn import cluster
# lien pour les fonctions de clustering https://scikit-learn.org/stable/auto_examples/cluster/plot_cluster_comparison.html


def situations_recording(clustering_metrics: List, sequences_number: int, create_simulation: Callable, consumption_options: List, production_options: List, complement_path: str, random_seed: int = 0):
    print(f"creation of the situation set")
    raw_situations = {key: [] for key in clustering_metrics}
    for i in range(sequences_number):
        print(f"year {i} of batch")
        metrics_datalogger = create_simulation(8760, random_order_priorities(consumption_options),
                                               random_order_priorities(production_options), f"{complement_path}/clustering/sequence_{i}",
                                               clustering_metrics, delay_days=i, random_seed=random_seed, standard_deviation=0.1)
        # récupérer moyennes pour normaliser métriques
        for key in clustering_metrics:
            raw_situations[key] = raw_situations[key] + metrics_datalogger._values[key]
    print("Done\n")

    return raw_situations


def clustering(clusters_number: int, clustering_metrics: List, raw_situations, sequences_number: int, random_seed: int = 0):
    print(f"construction of the description of the situations")
    sequences_number *= 8760
    refined_situations = np.zeros((sequences_number, len(clustering_metrics)))
    normalisation_values = []
    j = 0
    new_raw_situations = np.zeros((sequences_number, len(clustering_metrics)))
    for key, recorded_values in raw_situations.items():
        key_mean = np.mean(recorded_values)
        normalisation_values.append(key_mean)
        for i in range(sequences_number):
            refined_situations[i][j] = recorded_values[i]/key_mean
            new_raw_situations[i][j] = recorded_values[i]
        j += 1
    print("Done\n")

    # cluster centers initialisation
    np.random.seed(seed=random_seed)
    initial_clusters = np.zeros((clusters_number, len(clustering_metrics)))
    for i in range(len(clustering_metrics)):
        metric_min = min(refined_situations[:, i])
        metric_max = max(refined_situations[:, i])
        for j in range(clusters_number):
            initial_clusters[j, i] = np.random.random() * (metric_max-metric_min) + metric_min

    print(f"identification of clusters")
    clusters = cluster.AgglomerativeClustering(n_clusters=clusters_number, linkage="single").fit(refined_situations)

    # réassocier labels et metriques
    toto = clusters.labels_.tolist()
    tutu = new_raw_situations.tolist()
    titi = [[] for _ in range(clusters_number)]
    tata = []

    for i in range(len(refined_situations)):
        titi[toto[i]].append(tutu[i])
    for i in range(clusters_number):
        if len(titi[i]) > 10:
            clusters_centers = cluster.KMeans(10, max_iter=1500, tol=1e-6).fit(titi[i]).cluster_centers_.tolist()
        else:
            clusters_centers = titi[i]
        for j in range(len(clusters_centers)):
            clusters_centers[j].append(i)
        tata.append(clusters_centers)

    # ordonner les cluster dans l'ordre croissant du nombre de séquences qui y sont incluses
    print("sorting of cluster by size")
    # number of sequences by cluster
    clusters_label = clusters.labels_.tolist()
    sequences_count = [clusters_label.count(i) for i in range(clusters_number)]
    # sorting of clusters
    cluster_rank = [0 for _ in range(clusters_number)]
    sorted_cluster_centers = []
    for i in range(len(tata)):
        rank = 0
        for j in range(len(tata)):
            if sequences_count[j] <= sequences_count[i] and i != j:
                rank += 1
        cluster_rank[rank] = i
    cond = True
    while cond:  # enlever les doublons
        cond = False
        for i in range(len(cluster_rank)):
            for j in range(len(cluster_rank)):
                if i != j and cluster_rank[i] == cluster_rank[j]:
                    cluster_rank[i] += 1
                    cond = True
    for i in cluster_rank:
        sorted_cluster_centers += tata[i]
    sequences_count = sorted(sequences_count)
    print("Done\n")

    print(f"cluster centers: {sorted_cluster_centers}")
    # print(sequences_count)
    print("\n\n")

    def find_cluster(strategy: "Strategy"):
        current_situation = [strategy._catalog.get(key) for key in clustering_metrics]
        distance_min = math.inf
        for i in range(len(sorted_cluster_centers)):
            center = sorted_cluster_centers[i]
            distance = sum([(center[j] - current_situation[j]) ** 2 for j in range(len(clustering_metrics))])
            if distance < distance_min:
                distance_min = distance
                cluster_id = center[-1]  # the cluster the center belongs to
        return cluster_id

    return sorted_cluster_centers, sequences_count, find_cluster
