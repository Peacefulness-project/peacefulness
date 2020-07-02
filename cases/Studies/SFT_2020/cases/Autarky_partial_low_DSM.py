# first run for SFT 2020
# Exchange strategy: Autarky
# Distribution strategy: Partial
# Contract: 67 Normal, 20 DLC, 13 Curtailment


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.SFT_2020.Script import simulation

# parameters
exchange_strategy = "Autarky"
distribution_strategy = "Partial"
DSM_proportion = "low_DSM"

# simulation
world = simulation(exchange_strategy, distribution_strategy, DSM_proportion)



