# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.ECOS_collab_2021.Script import simulation

# parameters
name = "LCOERenewableFinal"
LCOE_HP = 0.144168
LCOE_renewable = 0.04877
solar_sizing = 0
biomass_sizing = 76.17

# simulation
world = simulation(name, solar_sizing, biomass_sizing, LCOE_HP, LCOE_renewable)








