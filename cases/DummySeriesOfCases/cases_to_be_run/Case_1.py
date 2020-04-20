# Main simulating instant consumption for the city of Marseille, in France, with the weather of Marseille

# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.DummySeriesOfCases.CaseBuildingBlocks import *

# parameters
chosen_strategy = "strategy_1"
renewable_capacity = "little"

# Importation of subclasses
subclasses_dictionary = get_subclasses()

# world and parameters
world = create_world_with_set_parameters(chosen_strategy, renewable_capacity)


# ##############################################################################################
# Model creation
# ##############################################################################################
# Strategies
strategies = create_strategies(chosen_strategy)

# Natures
natures = create_natures()

# Contracts
[contracts, price_IDs] = create_contracts(natures)

# Aggregators
aggregators = create_aggregators(natures, strategies)

# Agents
agents = create_agents()

# Devices
create_devices(world, aggregators, contracts, agents, price_IDs, renewable_capacity)

# Daemons
create_daemons(natures, price_IDs)

# Dataloggers
create_dataloggers()

# ##############################################################################################
# Simulation
# ##############################################################################################
world.start()




