# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.ECOS_collab_2021.Script import simulation

# parameters
name = "EnergyCOPEfficiencyFinal"
LCOE_HP = 0.34698
LCOE_renewable = 0.13193
solar_sizing = 13238.04/2
biomass_sizing = 76.17

# simulation
world = simulation(name, solar_sizing, biomass_sizing, LCOE_HP, LCOE_renewable)








