# Exchange strategy: autarky
# Contract: 50 Normal, 33 DLC, 17 Curtailment
# renewable sizing: mean


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.ECOS_collab_2020.Script import simulation

# parameters
chosen_strategy = "Autarky"
DSM_proportion = "low_DSM"
sizing = "mean"

# simulation
world = simulation(chosen_strategy, DSM_proportion, sizing)




