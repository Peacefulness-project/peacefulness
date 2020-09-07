# Exchange strategy: profitable
# Contract: 50 Normal, 33 DLC, 17 Curtailment
# renewable sizing: mean


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.LOCIE_1.Iteration_1.Script import simulation

# parameters
chosen_strategy = "Profitable"
DSM_proportion = "low_DSM"
sizing = "mean"

# simulation
world = simulation(chosen_strategy, DSM_proportion, sizing)



