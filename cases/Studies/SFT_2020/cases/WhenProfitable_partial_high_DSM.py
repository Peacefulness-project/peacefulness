# first run for SFT 2020
# Exchange strategy: Profitable
# Distribution strategy: Partial
# Contract: 33 Normal, 40 DLC, 27 Curtailment


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.SFT_2020.Script import simulation

# parameters
exchange_strategy = "Profitable"
distribution_strategy = "Partial"
DSM_proportion = "high_DSM"

# simulation
world = simulation(exchange_strategy, distribution_strategy, DSM_proportion)



