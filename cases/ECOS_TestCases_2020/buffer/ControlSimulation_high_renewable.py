# Exchange strategy: BAU
# Distribution strategy: BAU
# Contract: 100 Normal, 0 DLC, 0 Curtailment
# renewable sizing: high


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.ECOS_TestCases_2020.Script import simulation

# parameters
exchange_strategy = "BAU"
distribution_strategy = "BAU"
renewable_proportion = "high_renewable"
DSM_proportion = "no_DSM"

# simulation
world = simulation(exchange_strategy, distribution_strategy, renewable_proportion, DSM_proportion)


