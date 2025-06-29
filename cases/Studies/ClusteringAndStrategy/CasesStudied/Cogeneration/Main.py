from cases.Studies.ClusteringAndStrategy.CasesStudied.Cogeneration.Parameters import *
from cases.Studies.ClusteringAndStrategy.CasesStudied.Cogeneration.SimulationScript import create_simulation
from cases.Studies.ClusteringAndStrategy.EuclidianDistanceClustering import clustering, situations_recording
from cases.Studies.ClusteringAndStrategy.Training import training
from cases.Studies.ClusteringAndStrategy.Comparison import assess_performance, assess_reference


import time
import os

run_name = "final"
case = "Cogeneration"
results_path = f"cases/Studies/ClusteringAndStrategy/Results/{case}/{run_name}/"
if "Results" not in os.listdir("./cases/Studies/ClusteringAndStrategy"):
    os.mkdir("cases/Studies/ClusteringAndStrategy/Results/")
if case not in os.listdir("./cases/Studies/ClusteringAndStrategy/Results/"):
    os.mkdir(f"cases/Studies/ClusteringAndStrategy/Results/{case}/")
if run_name not in os.listdir(f"./cases/Studies/ClusteringAndStrategy/Results/{case}"):
    os.mkdir(f"cases/Studies/ClusteringAndStrategy/Results/{case}/{run_name}/")

intermediate_results = open(results_path + f"IntermediateResults_common.txt", "w")
ref_performance = assess_reference(comparison_simulation_length, performance_norm, ref_priorities_consumption,
                                   ref_priorities_production, exported_metrics, create_simulation)
intermediate_results.write("reference performance\n" + str(ref_performance) + "\n")
intermediate_results.close()

for i in range(3):  # seed for batch
    recorded_situations = situations_recording(clustering_metrics, clustering_batch_size, create_simulation, consumption_options, production_options, run_name, random_seed=i * 100)

    for j in range(3):  # seed for cluster initialisation
        # clustering
        intermediate_results = open(results_path + f"IntermediateResults_{i}_{j}.txt", "w")
        print("--- CLUSTERING PHASE ---")
        start_time = time.process_time()
        cluster_centers, center_sequences, find_cluster = clustering(cluster_number, clustering_metrics, recorded_situations, clustering_batch_size, random_seed=100 * j)
        intermediate_results.write("cluster centers:\n" + str(cluster_centers) + "\n")
        intermediate_results.write("center sequences:\n" + str(center_sequences) + "\n")
        clustering_duration = time.process_time() - start_time

        # training
        print("--- TRAINING PHASE ---")
        start_time = time.process_time()
        best_strategies, find_strategy_consumption, find_strategy_production = \
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
        cluster_along_time = open(results_path + f"ClustersALongTime_{0}.csv", "w")
        for moment, cluster in clusters_situation.items():
            cluster_along_time.write(f"{moment.strftime('%m,%d,%H')},{cluster}\n")
        cluster_along_time.close()
        comparison_duration = time.process_time() - start_time

        # post-treatment
        file = open(results_path + f"MesureDuTemps_{0}.txt", "w")
        file.write(f"temps training: {training_duration} s\n")
        file.write(f"temps comparaison: {comparison_duration} s\n")
        file.close()
