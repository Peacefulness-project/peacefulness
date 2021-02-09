# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.ECOS_CHP_2021.Script import simulation

# parameters
DSM_proportion = "little"
CHP_coverage_rate = 0.5

# simulation
world = simulation(DSM_proportion, CHP_coverage_rate)





