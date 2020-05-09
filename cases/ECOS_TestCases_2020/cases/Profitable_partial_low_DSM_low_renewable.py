# Exchange strategy: Profitable
# Distribution strategy: Partial
# Contract: 67 Normal, 20 DLC, 13 Curtailment
# renewable sizing: low


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.ECOS_TestCases_2020.Script import simulation

# parameters
exchange_strategy = "Profitable"
distribution_strategy = "Partial"
renewable_proportion = "low_renewable"
DSM_proportion = "low_DSM"

# simulation
world = simulation(exchange_strategy, distribution_strategy, renewable_proportion, DSM_proportion)



