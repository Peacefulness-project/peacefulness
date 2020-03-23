# first run for SFT 2020
# Exchange strategy: Autarky
# Distribution strategy: Partial
# Contract: 50 Normal, 30 DLC, 20 Curtailment


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.SFT_2020.CommonBlocks import *

# parameters
exchange_strategy = "Autarky"
distribution_strategy = "Partial"
DSM_proportion = "medium_DSM"

# Importation of subclasses
subclasses_dictionary = get_subclasses()

# world and parameters
world = create_world_with_set_parameters(exchange_strategy, distribution_strategy, DSM_proportion)


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
create_devices(world, aggregators, contracts, agents, price_IDs, DSM_proportion)

# Daemons
create_daemons(world, natures, price_IDs)

# Dataloggers
create_dataloggers(world)

# ##############################################################################################
# Simulation
# ##############################################################################################
world.start()



