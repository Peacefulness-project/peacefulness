# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.ECOS_collab_2021.Script import simulation

# parameters
name = "EnergyCOPEfficiency"
LCOE = 0.1987
solar_sizing = 14223.82/2
biomass_sizing = 76.17

# simulation
world = simulation(name, solar_sizing, biomass_sizing, LCOE)








