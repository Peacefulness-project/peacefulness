# Main simulating instant consumption for the city of Marseille, in France, with the weather of Marseille

# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Edwin_profiles.CommonBlocks import *

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
strategies = create_strategies(world)

# Natures
natures = create_natures(world)

# Contracts
price_IDs = create_contracts(world, natures)

# Aggregators
aggregators = create_aggregators(world, natures, strategies)

# Devices
create_devices(world, aggregators, price_IDs, country, city_weather)

# Daemons
create_daemons(world, natures, price_IDs, city_weather)

# Dataloggers
create_dataloggers(world)

# ##############################################################################################
# Simulation
# ##############################################################################################
world.start()




