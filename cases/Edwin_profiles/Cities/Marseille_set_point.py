# Main simulating instant consumption for the city of Marseille, in France, with the weather of Marseille

# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Edwin_profiles.CaseBuildingBlocks import *

# parameters
# prices = "France"
habits = "France"
city_weather = "Marseille"
set_point = "Spain"

# Importation of subclasses
subclasses_dictionary = get_subclasses()

# world and parameters
world = create_world_with_set_parameters(habits, city_weather, set_point)


# ##############################################################################################
# Model creation
# ##############################################################################################
# Strategies
strategies = create_strategies()

# Natures
natures = create_natures()

# Daemons
price_managing_daemons = create_daemons(natures, city_weather)

# Contracts
contracts = create_contracts(natures, price_managing_daemons)

# Aggregators
aggregators = create_aggregators(natures, strategies)

# Devices
create_devices(world, aggregators, price_managing_daemons, city_weather, habits, set_point)

# Dataloggers
create_dataloggers()


# ##############################################################################################
# Simulation
# ##############################################################################################
world.start()




