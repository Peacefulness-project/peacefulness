# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.DummySeriesOfCases.Script import simulation

# parameters
chosen_strategy = "strategy_1"
renewable_capacity = "little"

# simulation
world = simulation(chosen_strategy, renewable_capacity)




