# first run for SFT 2020
# Exchange strategy: Autarky
# Distribution strategy: Partial
# Contract: 50 Normal, 30 DLC, 20 Curtailment


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.SFT_2020.Script import simulation

# parameters
exchange_strategy = "Autarky"
distribution_strategy = "Partial"
DSM_proportion = "medium_DSM"

# simulation
world = simulation(exchange_strategy, distribution_strategy, DSM_proportion)



