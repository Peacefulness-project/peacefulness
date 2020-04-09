# Main simulating instant consumption for the city of Marseille, in France, with the weather of Marseille

# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Edwin_profiles.CaseBuildingBlocks import *

# parameters
country = "France"
city_case = "Marseille"
city_weather = "Marseille"

# Importation of subclasses
subclasses_dictionary = get_subclasses()

# world and parameters
world = create_world_with_set_parameters(city_case, city_weather)


# ##############################################################################################
# Model creation
# ##############################################################################################
# Strategies
strategies = create_strategies()

# Natures
natures = create_natures()

# Contracts
price_IDs = create_contracts(natures)

# Aggregators
aggregators = create_aggregators(natures, strategies)

# Devices
create_devices(world, aggregators, price_IDs, country, city_weather)

# Daemons
create_daemons(natures, price_IDs, city_weather)

# Dataloggers
create_dataloggers()

# ##############################################################################################
# Simulation
# ##############################################################################################
world.start()




