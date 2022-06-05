# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.EtudeDeCas2021.Script import simulation

# parameters
DSM_proportion = 40
strategy_exchange = "autarky"
strategy_distribution = "partial"
grid = "elec"

# simulation
world = simulation(DSM_proportion, strategy_exchange, strategy_distribution, grid)





