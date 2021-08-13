# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.ECOS_collab_2021.Script import simulation

# parameters
name = "LCOERenewable3"
LCOE = 0.13630
solar_sizing = 0
biomass_sizing = 76.17

# simulation
world = simulation(name, solar_sizing, biomass_sizing, LCOE)








