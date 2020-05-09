# Main simulating instant consumption for the city of Marseille, in France, with the weather of Marseille

# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Edwin_profiles.Script import simulation

# parameters
habits = "Spain"
city_weather = "Zaragoza"
set_point = "Spain"

# simulation
world = simulation(habits, city_weather, set_point)




