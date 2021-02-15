# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.ECOS_collab_2021.Script import simulation

# parameters
name = "EnergyEfficiency"
LCOE = 0.13094
solar_sizing = 0
biomass_sizing = 728.52

# simulation
world = simulation(name, solar_sizing, biomass_sizing, LCOE)








