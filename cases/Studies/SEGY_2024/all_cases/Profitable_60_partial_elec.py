# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.SEGY_2024.Script import simulation

# parameters
DSM_proportion = 60
strategy_exchange = "profitable"
strategy_distribution = "partial"
grid = "elec"

# simulation
world = simulation(DSM_proportion, strategy_exchange, strategy_distribution, grid)





