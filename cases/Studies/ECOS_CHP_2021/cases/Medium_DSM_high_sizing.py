# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.ECOS_CHP_2021.Script import simulation

# parameters
DSM_proportion = "medium"
CHP_coverage_rate = 0.9

# simulation
world = simulation(DSM_proportion, CHP_coverage_rate)





