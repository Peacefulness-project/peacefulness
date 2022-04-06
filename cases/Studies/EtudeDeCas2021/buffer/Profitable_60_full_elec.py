# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.EtudeDeCas2021.Script import simulation

# parameters
DSM_proportion = 60
strategy_exchange = "profitable"
strategy_distribution = "full"
grid = "elec"

# simulation
world = simulation(DSM_proportion, strategy_exchange, strategy_distribution, grid)





