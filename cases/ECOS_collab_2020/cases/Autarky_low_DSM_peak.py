# Exchange strategy: autarky
# Contract: 50 Normal, 33 DLC, 17 Curtailment
# renewable sizing: peak


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.ECOS_collab_2020.CaseBuildingBlocks import *

# parameters
chosen_strategy = "Autarky"
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
create_devices(world, aggregators, contracts, agents, price_IDs, DSM_proportion, sizing)

# Daemons
create_daemons(natures, price_IDs, sizing)

# Dataloggers
create_dataloggers()

# ##############################################################################################
# Simulation
# ##############################################################################################
world.start()




