from cases.Studies.ML.Parameters import *
from cases.Studies.ML.Clustering import clustering
from cases.Studies.ML.Training import training
from cases.Studies.ML.Comparison import comparison


# clustering
center_days, cluster_centers = clustering(training_simulation_length, cluster_number, clustering_metrics)


# training
best_strategies, performance_records = training(training_simulation_length, center_days, performance_norm, tested_strategies, performance_metrics)


# comparison
comparison(best_strategies, cluster_centers, clustering_metrics, comparison_simulation_length, performance_norm, tested_strategies, ref_priorities_consumption, ref_priorities_production)



