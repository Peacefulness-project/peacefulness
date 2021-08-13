# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.ECOS_collab_2021.Script import simulation

# parameters
name = "RenewableCoverageFinal"
LCOE_HP = 0.111334
LCOE_renewable = 0.11334
solar_sizing = 0
biomass_sizing = 3146.52

# simulation
world = simulation(name, solar_sizing, biomass_sizing, LCOE_HP, LCOE_renewable)








