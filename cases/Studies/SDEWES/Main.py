from cases.Studies.SDEWES.Parameters import *
from cases.Studies.SDEWES.SimulationScript import create_simulation
from cases.Studies.ClusteringAndStrategy.Clustering import clustering, situations_recording
from cases.Studies.ClusteringAndStrategy.Training import training
from cases.Studies.ClusteringAndStrategy.Comparison import assess_performance, assess_reference

import time
import os


results_path = "cases/Studies/SDEWES/Results/"
# export management
if "Results" not in os.listdir("./cases/Studies/SDEWES"):
    os.mkdir("cases/Studies/SDEWES/Results/")
if "HEMS" not in os.listdir("./cases/Studies/SDEWES/"):
    os.mkdir("cases/Studies/SDEWES/Results/HEMS/")
intermediate_results = open(results_path + f"IntermediateResults_common.txt", "w")


ref_performance = assess_reference(comparison_simulation_length, performance_norm, ref_priorities_consumption, ref_priorities_production, exported_metrics, create_simulation)
intermediate_results.write("reference performance\n" + str(ref_performance) + "\n")
intermediate_results.close()

recorded_situations = situations_recording(clustering_metrics, clustering_sequences_number, create_simulation, consumption_options, production_options)

for i in range(2, 10):
    cluster_number = i  # the number of clusters, fixed arbitrarily, can be determined studying the dispersion inside each cluster (see elbow method)
    intermediate_results = open(results_path + f"IntermediateResults_{i}_clusters.txt", "w")

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
    best_strategies = training(training_simulation_length, cluster_centers, performance_norm, exported_metrics, assessed_priorities, create_simulation, "HEMS", clustering_metrics)
    intermediate_results.write("best couples strategies/clusters:\n" + str(best_strategies) + "\n")
    training_duration = time.process_time() - start_time

    # comparison
    print("--- COMPARISON PHASE ---")
    start_time = time.process_time()
    tested_performance = assess_performance(best_strategies, cluster_centers, clustering_metrics, comparison_simulation_length, performance_norm, ref_priorities_consumption, ref_priorities_production, exported_metrics, create_simulation)
    intermediate_results.write("improved performance\n" + str(tested_performance) + "\n")
    intermediate_results.close()
    comparison_duration = time.process_time() - start_time

    # post-treatment
    file = open(results_path + f"MesureDuTemps_{i}_clusters.txt", "w")
    file.write(f"temps clustering: {clustering_duration} s\n")
    file.write(f"temps training: {training_duration} s\n")
    file.write(f"temps comparaison: {comparison_duration} s\n")
    file.close()



