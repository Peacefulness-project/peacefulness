# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.ECOS_CHP_2021.Script import simulation

# parameters
DSM_proportion = "no_DSM"
sizing = "little"

# simulation
world = simulation(DSM_proportion, sizing)





