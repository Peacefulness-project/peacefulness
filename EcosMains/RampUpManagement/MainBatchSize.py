from EcosMains.RampUpManagement.Parameters import *
from EcosMains.RampUpManagement.SimulationScript import create_simulation
from EuclidianDistanceClustering import clustering, situations_recording
from Training import training
from Comparison import assess_performance

import time
import os


# export management
run_name = "BatchSize"
case = "RampUpManagement"
results_path = f"cases/Studies/ClusteringAndStrategy/Results/{case}/{run_name}/"
if "Results" not in os.listdir("./cases/Studies/ClusteringAndStrategy"):
    os.mkdir("cases/Studies/ClusteringAndStrategy/Results/")
if case not in os.listdir("./cases/Studies/ClusteringAndStrategy/Results/"):
    os.mkdir(f"cases/Studies/ClusteringAndStrategy/Results/{case}/")
if run_name not in os.listdir(f"./cases/Studies/ClusteringAndStrategy/Results/{case}"):
    os.mkdir(f"cases/Studies/ClusteringAndStrategy/Results/{case}/{run_name}/")


for i in range(1, 11):
    recorded_situations = situations_recording(clustering_metrics, i, create_simulation, consumption_options, production_options, run_name)
    intermediate_results = open(results_path + f"IntermediateResults_{cluster_number}_clusters_{i}_batch_size.txt", "w")

    # clustering
    print("--- CLUSTERING PHASE ---")
    start_time = time.process_time()
    cluster_centers, center_sequences, find_cluster = clustering(cluster_number, clustering_metrics, recorded_situations, i)
    intermediate_results.write("cluster centers:\n" + str(cluster_centers) + "\n")
    intermediate_results.write("center sequences:\n" + str(center_sequences) + "\n")
    clustering_duration = time.process_time() - start_time

    # training
    print("--- TRAINING PHASE ---")
    start_time = time.process_time()
    best_strategies, find_strategy_consumption, find_strategy_production =\
        training(training_simulation_length, cluster_centers, performance_norm, exported_metrics, assessed_priorities,
                 create_simulation, find_cluster, case, run_name)
    intermediate_results.write("best couples strategies/clusters:\n" + str(best_strategies) + "\n")
    training_duration = time.process_time() - start_time

    # comparison
    print("--- COMPARISON PHASE ---")
    start_time = time.process_time()
    tested_performance, clusters_situation = \
        assess_performance(find_strategy_consumption, find_strategy_production, comparison_simulation_length,
                           performance_norm, exported_metrics, create_simulation, run_name)
    intermediate_results.write("improved performance\n" + str(tested_performance) + "\n")
    intermediate_results.close()

    # exporting the clusters to which each hour is attached
    cluster_along_time = open(results_path + f"ClustersALongTime_{i}.csv", "w")
    for moment, cluster in clusters_situation.items():
        cluster_along_time.write(f"{moment.strftime('%m,%d,%H')},{cluster}\n")
    cluster_along_time.close()
    comparison_duration = time.process_time() - start_time

    # post-treatment
    file = open(results_path + f"MesureDuTemps_{i}.txt", "w")
    file.write(f"temps clustering: {clustering_duration} s\n")
    file.write(f"temps training: {training_duration} s\n")
    file.write(f"temps comparaison: {comparison_duration} s\n")
    file.close()



