# first run for SFT 2020
# Exchange strategy: Autarky
# Distribution strategy: Partial
# Contract: 100 Normal, 0 DLC, 0 Curtailment


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.SFT_2020.Script import simulation

# parameters
exchange_strategy = "Autarky"
distribution_strategy = "Partial"
DSM_proportion = "no_DSM"

# simulation
world = simulation(exchange_strategy, distribution_strategy, DSM_proportion)


