# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.ECOS_collab_2021.Script import simulation

# parameters
name = "LCOEGlobalFinal"
LCOE_HP = 1.17753
LCOE_renewable = 0.07209
solar_sizing = 0
biomass_sizing = 1661.42

# simulation
world = simulation(name, solar_sizing, biomass_sizing, LCOE_HP, LCOE_renewable)








