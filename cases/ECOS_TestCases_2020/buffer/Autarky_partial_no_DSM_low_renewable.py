# Exchange strategy: Autarky
# Distribution strategy: Partial
# Contract: 100 Normal, 0 DLC, 0 Curtailment
# renewable sizing: low


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.ECOS_TestCases_2020.Script import simulation

# parameters
exchange_strategy = "Autarky"
distribution_strategy = "Partial"
renewable_proportion = "low_renewable"
DSM_proportion = "no_DSM"

# simulation
world = simulation(exchange_strategy, distribution_strategy, renewable_proportion, DSM_proportion)



