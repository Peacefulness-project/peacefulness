from typing import *
from random import seed

from cases.Studies.ML. SimulationScript import create_simulation
# import gym  # RL library, https://www.gymlibrary.ml/
from cases.Studies.ML.Utilities import *
from cases.Studies.ML.Clustering import clustering
from cases.Studies.ML.Training import training
from cases.Studies.ML.Comparison import comparison

# situations_to_test = pd.read_csv("")
# situations_temporal_depth = 1  # manually set to test different results

# for line in situations_to_test:
#     start_date = line["start_date"]
#     create_simulation(start_date, situations_temporal_depth)


# parameters
training_simulation_length = 6
cluster_number = 10
def performance_norm(performance_vector: Dict)-> float: # TODO: choose norm
    return sum(performance_vector["general_aggregator.coverage_rate"])
random_seed = "tournesol"
seed(random_seed)
comparison_simulation_length = 876
clustering_metrics = [  # prices are not taken into account for now
    # meteo

    # storage
    "battery.energy_stored",
    # consumption
    "general_aggregator.minimum_energy_consumption",
    "general_aggregator.maximum_energy_consumption",
    # production
    "general_aggregator.minimum_energy_production",
    "general_aggregator.maximum_energy_production",
]  # + demand en attente

assessed_priorities = {
    "toto": {"consumption": dummy_order_priorities_conso(), "production": dummy_order_priorities_prod()},
    "tutu": {"consumption": dummy_order_priorities_conso(), "production": dummy_order_priorities_prod()},
    "titi": {"consumption": dummy_order_priorities_conso(), "production": dummy_order_priorities_prod()},
    }
# TODO: vrai problème de définition de l'espace des stratégies (espace évolutif, type recherche heuristique ? coûteux mais devrait fonctionner et moins coûteux qu'un test systématique)


# clustering
# center_days, cluster_centers = clustering(training_simulation_length, cluster_number, clustering_metrics)
cluster_centers = [[1420.0735461618162, 1538.8584822274622, 293.7220998116076, 1987.990548350777], [829.8196230065117, 570.6286587210659, 196.6008497611779, 1529.2818783307064], [523.0999280280705, 363.0226435947479, 782.377572835095, 1018.775660639323], [95.82876629303586, 445.2568574126057, 37.618225429437175, 136.1147760741373], [467.34800837897876, 331.3797840600085, 101.23482792621245, 384.82807146744597], [566.2629801598846, 372.2345245325936, 209.37369603295087, 1174.262190916733], [2491.687520069635, 1619.7776372536941, 4771.28563154689, 5907.225360559814], [822.6344018070299, 557.1719328731695, 788.4408728275554, 1178.0736644320489], [539.1946918091919, 374.09860540821586, 28.592564634202578, 760.0384376152359], [276.72078902443644, 300.9686013987179, 354.9854580824804, 481.92049920738293]]
center_days = [246, 109, 17, 11, 9, 28, 258, 13, 125, 8]


# training
# best_strategies, performance_records = training(training_simulation_length, center_days, performance_norm, assessed_priorities)
performance_record = {0: {'center': 246, 'assessed_strategy': ['toto', 'tutu', 'titi'], 'performance': [0.17576837684972388, 0.17576837684972388, 0.17576837684972388]}, 1: {'center': 109, 'assessed_strategy': ['toto', 'tutu', 'titi'], 'performance': [4.928528485675323, 5.472322976452825, 5.472322976452825]}, 2: {'center': 17, 'assessed_strategy': ['toto', 'tutu', 'titi'], 'performance': [5.285231173304049, 5.285231173304049, 5.285231173304049]}, 3: {'center': 11, 'assessed_strategy': ['toto', 'tutu', 'titi'], 'performance': [4.599259845092623, 5.287652593730795, 5.287652593730795]}, 4: {'center': 9, 'assessed_strategy': ['toto', 'tutu', 'titi'], 'performance': [4.878792326795459, 5.255527452609093, 5.255527452609093]}, 5: {'center': 28, 'assessed_strategy': ['toto', 'tutu', 'titi'], 'performance': [5.189130378823012, 5.282551388162441, 5.282551388162441]}, 6: {'center': 258, 'assessed_strategy': ['toto', 'tutu', 'titi'], 'performance': [3.4562964136003393, 3.4562964136003393, 3.4562964136003393]}, 7: {'center': 13, 'assessed_strategy': ['toto', 'tutu', 'titi'], 'performance': [4.696702353411092, 5.291722909685172, 5.291722909685172]}, 8: {'center': 125, 'assessed_strategy': ['toto', 'tutu', 'titi'], 'performance': [4.8072272967239424, 5.325595075609613, 5.325595075609613]}, 9: {'center': 8, 'assessed_strategy': ['toto', 'tutu', 'titi'], 'performance': [4.699028836752135, 5.253874671656014, 5.253874671656014]}}
best_strategies = {0: (0.17576837684972388, 'toto'), 1: (5.472322976452825, 'tutu'), 2: (5.285231173304049, 'toto'), 3: (5.287652593730795, 'tutu'), 4: (5.255527452609093, 'tutu'), 5: (5.282551388162441, 'tutu'), 6: (3.4562964136003393, 'toto'), 7: (5.291722909685172, 'tutu'), 8: (5.325595075609613, 'tutu'), 9: (5.253874671656014, 'tutu')}


# comparison
comparison(best_strategies, cluster_centers, clustering_metrics, comparison_simulation_length, performance_norm, assessed_priorities)



