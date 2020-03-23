# first run for SFT 2020
# Exchange strategy: Profitable
# Distribution strategy: Emergency
# Contract: 33 Normal, 40 DLC, 27 Curtailment
# renewable sizing: low


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.ECOS_TestCases_2020.CommonBlocks import *

# parameters
exchange_strategy = "Profitable"
distribution_strategy = "Emergency"
renewable_proportion = "low_renewable"
DSM_proportion = "high_DSM"

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



