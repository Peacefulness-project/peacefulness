# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.ECOS_collab_2021.Script import simulation

# parameters
name = "LCOERenewable"
LCOE = 0.11187
solar_sizing = 0
biomass_sizing = 728.52

# simulation
world = simulation(name, solar_sizing, biomass_sizing, LCOE)








