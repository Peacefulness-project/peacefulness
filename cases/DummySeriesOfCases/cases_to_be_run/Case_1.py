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

# Daemons
price_managing_daemons = create_daemons(natures)

# Aggregators
aggregators = create_aggregators(natures, strategies)

# Agents
agents = create_agents()

# Contracts
contracts = create_contracts(natures, price_managing_daemons)

# Devices
create_devices(world, aggregators, contracts, agents, price_managing_daemons, renewable_capacity)

# Dataloggers
create_dataloggers()

# ##############################################################################################
# Simulation
# ##############################################################################################
world.start()




