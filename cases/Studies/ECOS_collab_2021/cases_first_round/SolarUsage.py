# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.ECOS_collab_2021.Script import simulation

# parameters
name = "SolarUsage"
LCOE = 0.12007
solar_sizing = 2541.66/2
biomass_sizing = 728.52

# simulation
world = simulation(name, solar_sizing, biomass_sizing, LCOE)








