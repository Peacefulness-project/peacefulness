# Exchange strategy: Profitable
# Distribution strategy: Partial
# Contract: 33 Normal, 40 DLC, 27 Curtailment
# renewable sizing: high


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.ECOS_TestCases_2020.Script import simulation

# parameters
exchange_strategy = "Profitable"
distribution_strategy = "Partial"
renewable_proportion = "high_renewable"
DSM_proportion = "high_DSM"

# simulation
world = simulation(exchange_strategy, distribution_strategy, renewable_proportion, DSM_proportion)



