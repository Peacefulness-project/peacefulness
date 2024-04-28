# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.SEGY_2024.Script import simulation

# parameters
DSM_proportion = 40
strategy_exchange = "autarky"
strategy_distribution = "partial"
grid = "elec"

# simulation
world = simulation(DSM_proportion, strategy_exchange, strategy_distribution, grid)





