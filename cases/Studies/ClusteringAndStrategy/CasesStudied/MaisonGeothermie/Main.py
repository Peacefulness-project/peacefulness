from cases.Studies.ClusteringAndStrategy.CasesStudied.MaisonGeothermie.Parameters import *
from cases.Studies.ClusteringAndStrategy.CasesStudied.MaisonGeothermie.SimulationScript import create_simulation
from cases.Studies.ClusteringAndStrategy.EuclidianDistanceClustering import clustering
from cases.Studies.ClusteringAndStrategy.Training import training
from cases.Studies.ClusteringAndStrategy.Comparison import assess_performance

import time


import time
import os


results_path = "cases/Studies/ClusteringAndStrategy/Results/MaisonGeothermie/"
if "Results" not in os.listdir("./cases/Studies/ClusteringAndStrategy"):
    os.mkdir("cases/Studies/ClusteringAndStrategy/Results/")
if "LimitedResource" not in os.listdir("./cases/Studies/ClusteringAndStrategy/Results/"):
    os.mkdir("cases/Studies/ClusteringAndStrategy/Results/MaisonGeothermie/")
intermediate_results = open(results_path + "IntermediateResults.txt", "w")


start_time = time.process_time()
# clustering
print("--- CLUSTERING PHASE ---")
cluster_centers, center_sequences = clustering(1, cluster_number, clustering_metrics, sequences_number, gap, create_simulation, consumption_options, production_options)
intermediate_results.write("cluster centers:\n" + str(cluster_centers) + "\n")
intermediate_results.write("center sequences:\n" + str(center_sequences) + "\n")
clustering_duration = time.process_time() - start_time


start_time = time.process_time()
# training
print("--- TRAINING PHASE ---")
best_strategies = training(training_simulation_length, cluster_centers, performance_norm, exported_metrics, assessed_priorities, create_simulation, "MaisonGeothermie", clustering_metrics)
intermediate_results.write("best couples strategies/clusters:\n" + str(best_strategies) + "\n")
training_duration = time.process_time() - start_time


start_time = time.process_time()
# comparison
print("--- COMPARISON PHASE ---")
assess_performance(best_strategies, cluster_centers, clustering_metrics, comparison_simulation_length, performance_norm, ref_priorities_consumption, ref_priorities_production, exported_metrics, create_simulation)
intermediate_results.close()
comparison_duration = time.process_time() - start_time


# post-treatment
file = open(results_path + "MesureDuTemps.txt", "w")
# file.write(f"temps clustering: {clustering_duration} s\n")
file.write(f"temps training: {training_duration} s\n")
file.write(f"temps comparaison: {comparison_duration} s\n")
file.close()
