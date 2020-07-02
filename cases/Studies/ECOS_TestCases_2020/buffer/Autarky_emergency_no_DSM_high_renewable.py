# Exchange strategy: Autarky
# Distribution strategy: Emergency
# Contract: 100 Normal, 0 DLC, 0 Curtailment
# renewable sizing: high


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.ECOS_TestCases_2020.Script import simulation

# parameters
exchange_strategy = "Autarky"
distribution_strategy = "Emergency"
renewable_proportion = "high_renewable"
DSM_proportion = "no_DSM"

# simulation
world = simulation(exchange_strategy, distribution_strategy, renewable_proportion, DSM_proportion)


