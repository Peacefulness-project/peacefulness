# Exchange strategy: autarky
# Contract: 33 Normal, 40 DLC, 27 Curtailment
# renewable sizing: peak


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.LOCIE_1.Script import simulation

# parameters
chosen_strategy = "Autarky"
DSM_proportion = "high_DSM"
sizing = "peak"

# simulation
world = simulation(chosen_strategy, DSM_proportion, sizing)



