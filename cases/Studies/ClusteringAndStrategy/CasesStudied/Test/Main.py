from cases.Studies.ClusteringAndStrategy.CasesStudied.Test.Parameters import *
from cases.Studies.ClusteringAndStrategy.CasesStudied.Test.SimulationScript import create_simulation
from cases.Studies.ClusteringAndStrategy.Clustering import clustering
from cases.Studies.ClusteringAndStrategy.Training import training
from cases.Studies.ClusteringAndStrategy.Comparison import assess_performance

# # clustering
# print("--- CLUSTERING PHASE ---")
# cluster_centers, center_days = clustering(training_simulation_length, cluster_number, clustering_metrics, days_number, gap, create_simulation, consumption_options, production_options)
cluster_centers = [[497.33799733333336, 85.58566996838681, 663.5450934666383, 62.2926707934375, 1058.0971050073126], [497.753498, 232.00547493568502, 752.2975838189274, 558.230102834625, 787.921519597875], [498.99999999999994, 679.7276246412889, 1954.3660076258975, 61.513977359250006, 988.8289527285002]]
center_days = [10, 1, 4]

# training
print("--- TRAINING PHASE ---")
best_strategies = training(training_simulation_length, cluster_centers, performance_norm, performance_metrics, assessed_priorities, create_simulation, "TestCase", clustering_metrics)


# comparison
print("--- COMPARISON PHASE ---")
assess_performance(best_strategies, cluster_centers, center_days, clustering_metrics, comparison_simulation_length, performance_norm, assessed_priorities, ref_priorities_consumption, ref_priorities_production, performance_metrics, create_simulation)



