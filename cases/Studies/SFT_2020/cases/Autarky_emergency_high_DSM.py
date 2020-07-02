# Exchange strategy: Autarky
# Distribution strategy: Emergency
# Contract: 33 Normal, 40 DLC, 27 Curtailment


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.SFT_2020.Script import simulation

# parameters
exchange_strategy = "Autarky"
distribution_strategy = "Emergency"
DSM_proportion = "high_DSM"

# simulation
world = simulation(exchange_strategy, distribution_strategy, DSM_proportion)



