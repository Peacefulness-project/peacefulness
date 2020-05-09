# Exchange strategy: Autarky
# Distribution strategy: Emergency
# Contract: 33 Normal, 40 DLC, 27 Curtailment
# renewable sizing: low


# ##############################################################################################
# Initialization
# ###############################################################################################
# Importation
from cases.ECOS_TestCases_2020.Script import simulation

# parameters
exchange_strategy = "Autarky"
distribution_strategy = "Emergency"
renewable_proportion = "low_renewable"
DSM_proportion = "high_DSM"

# simulation
world = simulation(exchange_strategy, distribution_strategy, renewable_proportion, DSM_proportion)



