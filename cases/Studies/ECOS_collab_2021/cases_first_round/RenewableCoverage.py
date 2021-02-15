# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.ECOS_collab_2021.Script import simulation

# parameters
name = "RenewableCoverage"
LCOE = 0.11503
solar_sizing = 0
biomass_sizing = 3146.52

# simulation
world = simulation(name, solar_sizing, biomass_sizing, LCOE)








