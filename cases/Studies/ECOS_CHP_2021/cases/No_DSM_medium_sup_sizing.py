# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.ECOS_CHP_2021.Script import simulation

# parameters
DSM_proportion = "no_DSM"
CHP_coverage_rate = 0.7

# simulation
world = simulation(DSM_proportion, CHP_coverage_rate)





