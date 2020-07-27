# Exchange strategy: autarky
# Contract: 100 Normal, 0 DLC, 0 Curtailment
# renewable sizing: mean


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.LOCIE_1.Script import simulation

# parameters
chosen_strategy = "Autarky"
DSM_proportion = "no_DSM"
sizing = "mean"

# simulation
world = simulation(chosen_strategy, DSM_proportion, sizing)




