# first run for SFT 2020
# Exchange strategy: profitable
# Contract: 50 Normal, 33 DLC, 17 Curtailment
# renewable sizing: peak


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.ECOS_collab_2020.CaseBuildingBlocks import *

# parameters
chosen_strategy = "Profitable"
DSM_proportion = "low_DSM"
sizing = "peak"

# Importation of subclasses
subclasses_dictionary = get_subclasses()

# world and parameters
world = create_world_with_set_parameters(chosen_strategy, DSM_proportion, sizing)


# ##############################################################################################
# Model creation
# ##############################################################################################
# Strategies
strategies = create_strategies(world, chosen_strategy)

# Natures
natures = create_natures(world)

# Contracts
[contracts, price_IDs] = create_contracts(world, natures)

# Aggregators
aggregators = create_aggregators(world, natures, strategies)

# Agents
agents = create_agents(world)

# Devices
create_devices(world, aggregators, contracts, agents, price_IDs, DSM_proportion, sizing)

# Daemons
create_daemons(world, natures, price_IDs, sizing)

# Dataloggers
create_dataloggers(world)

# ##############################################################################################
# Simulation
# ##############################################################################################
world.start()



