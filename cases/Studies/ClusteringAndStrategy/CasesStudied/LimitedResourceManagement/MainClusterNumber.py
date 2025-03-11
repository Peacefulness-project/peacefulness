from cases.Studies.ClusteringAndStrategy.CasesStudied.LimitedResourceManagement.Parameters import *
from cases.Studies.ClusteringAndStrategy.CasesStudied.LimitedResourceManagement.SimulationScript import create_simulation
from cases.Studies.ClusteringAndStrategy.Clustering import clustering, situations_recording
from cases.Studies.ClusteringAndStrategy.Training import training
from cases.Studies.ClusteringAndStrategy.Comparison import assess_performance, assess_reference

import time
import os


results_path = "cases/Studies/ClusteringAndStrategy/Results/LimitedResource/ClusterNumber/"
# export management
if "Results" not in os.listdir("./cases/Studies/ClusteringAndStrategy"):
    os.mkdir("cases/Studies/ClusteringAndStrategy/Results/")
if "LimitedResource" not in os.listdir("./cases/Studies/ClusteringAndStrategy/Results/"):
    os.mkdir("cases/Studies/ClusteringAndStrategy/Results/LimitedResource/")
if "ClusterNumber" not in os.listdir("./cases/Studies/ClusteringAndStrategy/Results/LimitedResource"):
    os.mkdir("cases/Studies/ClusteringAndStrategy/Results/LimitedResource/ClusterNumber/")

intermediate_results = open(results_path + f"IntermediateResults_common.txt", "w")
ref_performance = assess_reference(comparison_simulation_length, performance_norm, ref_priorities_consumption, ref_priorities_production, exported_metrics, create_simulation)
intermediate_results.write("reference performance\n" + str(ref_performance) + "\n")
intermediate_results.close()
recorded_situations = situations_recording(clustering_metrics, clustering_sequences_number, create_simulation, consumption_options, production_options, "ClusterNumber")


for i in range(2, 11):
    cluster_number = i  # the number of clusters, fixed arbitrarily, can be determined studying the dispersion inside each cluster (see elbow method)
    intermediate_results = open(results_path + f"IntermediateResults_{cluster_number}_clusters.txt", "w")

    # clustering
    print("--- CLUSTERING PHASE ---")
    start_time = time.process_time()
    cluster_centers, center_sequences, cluster_size = clustering(cluster_number, clustering_metrics, recorded_situations, clustering_sequences_number)
    intermediate_results.write("cluster centers:\n" + str(cluster_centers) + "\n")
    intermediate_results.write("center sequences:\n" + str(center_sequences) + "\n")
    intermediate_results.write("cluster cardinal:\n" + str(cluster_size) + "\n")
    clustering_duration = time.process_time() - start_time

    # training
    print("--- TRAINING PHASE ---")
    start_time = time.process_time()
    best_strategies = training(training_simulation_length, cluster_centers, performance_norm, exported_metrics, assessed_priorities, create_simulation, "LimitedResource", clustering_metrics, "ClusterNumber")
    intermediate_results.write("best couples strategies/clusters:\n" + str(best_strategies) + "\n")
    training_duration = time.process_time() - start_time

    # comparison
    best_strategies = {0: (-143185.05880108482, {'consumption': ['nothing', 'storage', 'industrial'], 'production': ['unstorage', 'production', 'grid']}), 1: (-143185.05880108482, {'consumption': ['industrial', 'nothing', 'storage'], 'production': ['unstorage', 'production', 'grid']}), 2: (-81232.20691225678, {'consumption': ['storage', 'industrial', 'nothing'], 'production': ['unstorage', 'production', 'grid']}), 3: (-4.476419235288631e-11, {'consumption': ['nothing', 'storage', 'industrial'], 'production': ['unstorage', 'production', 'grid']})}
    cluster_centers = [[274.3869442337913, 0.004615731515370519, 269.906141516992], [958.250967896316, 41.490874990554985, 69.29363058287564], [242.51395500606267, 295.32399168947916, 344.1957479888399], [336.93334645610616, 103.21495185671594, 112.46596114133183]]

    print("--- COMPARISON PHASE ---")
    start_time = time.process_time()
    tested_performance, clusters_situation = assess_performance(best_strategies, cluster_centers, clustering_metrics, comparison_simulation_length, performance_norm, ref_priorities_consumption, ref_priorities_production, exported_metrics, create_simulation, "ClusterNumber")
    intermediate_results.write("improved performance\n" + str(tested_performance) + "\n")
    intermediate_results.close()

    # exporting the clusters to which each hour is attached
    cluster_along_time = open(results_path + f"ClustersALongTime_{i}.csv", "w")
    for moment, cluster in clusters_situation.items():
        cluster_along_time.write(f"{moment.strftime('%m,%d,%H')},{cluster}\n")
    cluster_along_time.close()
    comparison_duration = time.process_time() - start_time

    # post-treatment
    file = open(results_path + f"MesureDuTemps_{i}_clusters.txt", "w")
    file.write(f"temps clustering: {clustering_duration} s\n")
    file.write(f"temps training: {training_duration} s\n")
    file.write(f"temps comparaison: {comparison_duration} s\n")
    file.close()



