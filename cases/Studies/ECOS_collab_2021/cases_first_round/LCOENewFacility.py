# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.ECOS_collab_2021.Script import simulation

# parameters
name = "LCOENewFacility"
LCOE = 0.10973
solar_sizing = 0
biomass_sizing = 970.32

# simulation
world = simulation(name, solar_sizing, biomass_sizing, LCOE)








