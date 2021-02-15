# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.ECOS_collab_2021.Script import simulation

# parameters
name = "ExergyCOPEfficiency"
LCOE = 0.20178
solar_sizing = 18355.05/2
biomass_sizing = 728.52

# simulation
world = simulation(name, solar_sizing, biomass_sizing, LCOE)








