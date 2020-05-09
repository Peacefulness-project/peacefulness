# Main simulating instant consumption for the city of Marseille, in France, with the weather of Marseille

# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Edwin_profiles.Script import simulation

# parameters
# prices = "France"
habits = "France"
city_weather = "Marseille"
set_point = "France"

# simulation
world = simulation(habits, city_weather, set_point)



