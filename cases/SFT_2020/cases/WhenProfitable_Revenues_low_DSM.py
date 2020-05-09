# first run for SFT 2020
# Exchange strategy: Profitable
# Distribution strategy: Revenues
# Contract: 67 Normal, 20 DLC, 13 Curtailment


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.SFT_2020.Script import simulation

# parameters
exchange_strategy = "Profitable"
distribution_strategy = "Revenues"
DSM_proportion = "low_DSM"

# simulation
world = simulation(exchange_strategy, distribution_strategy, DSM_proportion)



