# Exchange strategy: profitable
# Contract: 50 Normal, 33 DLC, 17 Curtailment
# renewable sizing: peak


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.LOCIE_1.Script import simulation

# parameters
chosen_strategy = "Profitable"
DSM_proportion = "low_DSM"
sizing = "peak"

# simulation
world = simulation(chosen_strategy, DSM_proportion, sizing)



