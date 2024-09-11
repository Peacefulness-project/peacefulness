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
best_strategies = training(training_simulation_length, center_sequences, performance_norm, performance_metrics, assessed_priorities, create_simulation)


# comparison
print("--- COMPARISON PHASE ---")
# comparison(best_strategies, cluster_centers, center_sequences, clustering_metrics, comparison_simulation_length, performance_norm, assessed_priorities, ref_priorities_consumption, ref_priorities_production, performance_metrics, create_simulation)


best_strategies = {4060: (193.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   5857: (184.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   3952: (193.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   5513: (175.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   3503: (202.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   6549: (184.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   6267: (184.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   3131: (202.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   8063: (211.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   5409: (175.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   5073: (184.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   6219: (184.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   882:  (229.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   6257: (184.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   3436: (202.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   4062: (193.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   8181: (211.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   5539: (175.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   2936: (202.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   2873: (211.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   8656: (211.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   7623: (202.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   8653: (211.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   4482: (184.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   4689: (184.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   4751: (184.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   3011: (202.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   4195: (193.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   1217: (229.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']}),
                   4351: (184.5, {'consumption': ['spatial_heating', 'long_term_storage'], 'production': ['long_term_unstorage', 'heat_pump']})
                   }
