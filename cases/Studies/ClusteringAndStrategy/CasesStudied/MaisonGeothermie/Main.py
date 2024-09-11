from cases.Studies.ClusteringAndStrategy.CasesStudied.MaisonGeothermie.Parameters import *
from cases.Studies.ClusteringAndStrategy.CasesStudied.MaisonGeothermie.SimulationScript import create_simulation
from cases.Studies.ClusteringAndStrategy.Clustering import clustering
from cases.Studies.ClusteringAndStrategy.Training import training
from cases.Studies.ClusteringAndStrategy.Comparison import comparison

# clustering
print("--- CLUSTERING PHASE ---")
cluster_centers, center_sequences = clustering(training_simulation_length, cluster_number, clustering_metrics, sequences_number, gap, create_simulation, consumption_options, production_options)


# training
print("--- TRAINING PHASE ---")
best_strategies = training(training_simulation_length, center_sequences, training_performance_norm, performance_metrics, assessed_priorities, create_simulation)


# comparison
print("--- COMPARISON PHASE ---")
comparison(best_strategies, cluster_centers, center_sequences, clustering_metrics, comparison_simulation_length, comparison_performance_norm, assessed_priorities, ref_priorities_consumption, ref_priorities_production, performance_metrics, create_simulation)
