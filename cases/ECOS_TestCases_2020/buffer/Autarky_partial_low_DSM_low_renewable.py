# first run for SFT 2020
# Exchange strategy: Autarky
# Distribution strategy: Partial
# Contract: 67 Normal, 20 DLC, 13 Curtailment
# renewable sizing: low


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.ECOS_TestCases_2020.CaseBuildingBlocks import *

# parameters
exchange_strategy = "Autarky"
distribution_strategy = "Partial"
renewable_proportion = "low_renewable"
DSM_proportion = "low_DSM"

# Importation of subclasses
subclasses_dictionary = get_subclasses()

# world and parameters
world = create_world_with_set_parameters(exchange_strategy, distribution_strategy, renewable_proportion, DSM_proportion)


# ##############################################################################################
# Model creation
# ##############################################################################################
# Strategies
strategies = create_strategies(world, exchange_strategy, distribution_strategy)

# Natures
natures = create_natures(world)

# Contracts
[contracts, price_IDs] = create_contracts(world, natures)

# Aggregators
aggregators = create_aggregators(world, natures, strategies)

# Agents
agents = create_agents(world)

# Devices
create_devices(world, aggregators, contracts, agents, price_IDs, DSM_proportion, renewable_proportion)

# Daemons
create_daemons(world, natures, price_IDs)

# Dataloggers
create_dataloggers(world, renewable_proportion)

# ##############################################################################################
# Simulation
# ##############################################################################################
world.start()



