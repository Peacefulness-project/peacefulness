# Exchange strategy: Autarky
# Distribution strategy: Emergency
# Contract: 67 Normal, 20 DLC, 13 Curtailment
# renewable sizing: low


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.ECOS_TestCases_2020.Script import simulation

# parameters
exchange_strategy = "Autarky"
distribution_strategy = "Emergency"
renewable_proportion = "low_renewable"
DSM_proportion = "low_DSM"

# simulation
world = simulation(exchange_strategy, distribution_strategy, renewable_proportion, DSM_proportion)



