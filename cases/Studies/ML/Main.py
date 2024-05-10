from cases.Studies.ML.Parameters import *
from cases.Studies.ML.Clustering import clustering
from cases.Studies.ML.Training import training
from cases.Studies.ML.Comparison import comparison

# # clustering
# print("--- CLUSTERING PHASE ---")
# cluster_centers, center_days = clustering(training_simulation_length, cluster_number, clustering_metrics, days_number, gap)


# training
cluster_centers = [[2240.243559023258, 1587.952784926485, 260.56302562190734, 4057.3744694819798], [380.3478934125518, 420.8019048338359, 107.15036417444881, 285.80039192954246], [327.40138360198864, 381.5875877936067, 30.630186019455394, 511.72017731945283], [435.11718778096946, 335.04511352432655, 408.7226707205579, 615.0100756403278], [318.33569325217826, 352.19405291097013, 22.43166924624506, 432.39857213503865], [471.73325789382017, 449.43679106139024, 166.54488275533558, 425.8350649788693], [149.70973440704856, 682.4989875504272, 62.00313384757453, 268.61560369537517], [885.8331947957134, 536.6122270499045, 1003.9198927792897, 1420.0177747166742], [343.6655644834855, 637.6710110520984, 84.05074322131841, 372.84019675677865], [757.5819801005216, 662.2508960825569, 81.91647320272223, 1216.3476164937122]]
center_days = [50, 13, 39, 3, 13, 5, 16, 1, 16, 51]
print("--- TRAINING PHASE ---")
best_strategies = training(training_simulation_length, center_days, performance_norm, performance_metrics, assessed_priorities)


# comparison
best_strategies = [(-0.9412973680776848, {"consumption": ['store', 'soft_DSM_conso', 'hard_DSM_conso', 'buy_outside_emergency'],
                                              "production": ['unstore', 'sell_outside_emergency', 'soft_DSM_prod', 'hard_DSM_prod']}),
                   (-0.893726727284143, {"consumption": ['store', 'buy_outside_emergency', 'hard_DSM_conso', 'soft_DSM_conso'],
                                             "production": ['unstore', 'hard_DSM_prod', 'soft_DSM_prod', 'sell_outside_emergency']}),
                   (-0.973709853717003, {"consumption": ['store', 'buy_outside_emergency', 'soft_DSM_conso', 'hard_DSM_conso'],
                                             "production": ['unstore', 'sell_outside_emergency', 'hard_DSM_prod', 'soft_DSM_prod']}),
                   (-0.9667664374981276, {"consumption": ['store', 'buy_outside_emergency', 'soft_DSM_conso', 'hard_DSM_conso'],
                                             "production": ['unstore', 'sell_outside_emergency', 'soft_DSM_prod', 'hard_DSM_prod']}),
                   (-0.9439239958578671, {"consumption": ['store', 'soft_DSM_conso', 'hard_DSM_conso', 'buy_outside_emergency'],
                                             "production": ['unstore', 'sell_outside_emergency', 'hard_DSM_prod', 'soft_DSM_prod']}),
                   (-0.8690267828075432, {"consumption": ['store', 'buy_outside_emergency', 'soft_DSM_conso', 'hard_DSM_conso'],
                                              "production": ['unstore', 'sell_outside_emergency', 'soft_DSM_prod', 'hard_DSM_prod']}),
                   (-0.7462118868647752, {"consumption": ['store', 'soft_DSM_conso', 'buy_outside_emergency', 'hard_DSM_conso'],
                                             "production": ['unstore', 'sell_outside_emergency', 'soft_DSM_prod', 'hard_DSM_prod']}),
                   (-0.9633949518772721, {"consumption": ['store', 'buy_outside_emergency', 'hard_DSM_conso', 'soft_DSM_conso'],
                                              "production": ['unstore', 'sell_outside_emergency', 'hard_DSM_prod', 'soft_DSM_prod']})
                   ]
# print("--- COMPARISON PHASE ---")
# comparison(best_strategies, cluster_centers, clustering_metrics, comparison_simulation_length, performance_norm, assessed_priorities, ref_priorities_consumption, ref_priorities_production, performance_metrics)



