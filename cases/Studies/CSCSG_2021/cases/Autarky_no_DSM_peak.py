# Exchange strategy: autarky
# Contract: 100 Normal, 0 DLC, 0 Curtailment
# renewable sizing: peak


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.ECOS_collab_2020.Script import simulation

# parameters
chosen_strategy = "Autarky"
DSM_proportion = "no_DSM"
sizing = "peak"

# simulation
world = simulation(chosen_strategy, DSM_proportion, sizing)




