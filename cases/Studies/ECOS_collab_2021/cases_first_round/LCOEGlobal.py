# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.ECOS_collab_2021.Script import simulation

# parameters
name = "LCOEGlobal"
LCOE = 0.10721
solar_sizing = 0
biomass_sizing = 1695.72

# simulation
world = simulation(name, solar_sizing, biomass_sizing, LCOE)








