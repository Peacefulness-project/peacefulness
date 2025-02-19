from cases.Studies.ClusteringAndStrategy.CasesStudied.LimitedResourceManagement.Parameters import *
from cases.Studies.ClusteringAndStrategy.CasesStudied.LimitedResourceManagement.SimulationScript import create_simulation
from cases.Studies.ClusteringAndStrategy.Clustering import clustering
from cases.Studies.ClusteringAndStrategy.Training import training
from cases.Studies.ClusteringAndStrategy.Comparison import comparison

import time
import datetime

file = open("cases/Studies/ClusteringAndStrategy/Results/LimitedResource/MesureDuTemps.txt", "w")

start_time = time.process_time()
# clustering
print("--- CLUSTERING PHASE ---")
cluster_centers, center_sequences = clustering(1, cluster_number, clustering_metrics, sequences_number, gap, create_simulation, consumption_options, production_options)
end_time = time.process_time()
file.write(f"temps clustering: {end_time - start_time} s\n")
file.write(f"heure:  {datetime.datetime.now()}\n\n")


start_time = time.process_time()
# training
print("--- TRAINING PHASE ---")
best_strategies = training(training_simulation_length, cluster_centers, performance_norm, performance_metrics, assessed_priorities, create_simulation, "LimitedResource", clustering_metrics)
end_time = time.process_time()
file.write(f"temps training: {end_time - start_time} s\n")
file.write(f"heure:  {datetime.datetime.now()}\n\n")


start_time = time.process_time()
# comparison
print("--- COMPARISON PHASE ---")
comparison(best_strategies, cluster_centers, clustering_metrics, comparison_simulation_length, performance_norm, ref_priorities_consumption, ref_priorities_production, performance_metrics, create_simulation)
end_time = time.process_time()
file.write(f"temps comparaison: {end_time - start_time} s\n")
file.write(f"heure:  {datetime.datetime.now()}\n\n")

file.close()
