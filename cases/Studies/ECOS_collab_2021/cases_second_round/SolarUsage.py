# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.ECOS_collab_2021.Script import simulation

# parameters
name = "SolarUsage"
LCOE = 0.14358
solar_sizing = 3191.34/2
biomass_sizing = 76.17

# simulation
world = simulation(name, solar_sizing, biomass_sizing, LCOE)








