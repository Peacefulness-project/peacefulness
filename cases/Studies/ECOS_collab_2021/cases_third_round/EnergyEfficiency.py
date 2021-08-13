# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.ECOS_collab_2021.Script import simulation

# parameters
name = "EnergyEfficiency3"
LCOE = 0.14026
solar_sizing = 0
biomass_sizing = 76.17

# simulation
world = simulation(name, solar_sizing, biomass_sizing, LCOE)








