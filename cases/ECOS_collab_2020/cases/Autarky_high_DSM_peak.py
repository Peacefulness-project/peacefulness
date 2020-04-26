# Exchange strategy: autarky
# Contract: 33 Normal, 40 DLC, 27 Curtailment
# renewable sizing: peak


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.ECOS_collab_2020.CaseBuildingBlocks import *

# parameters
chosen_strategy = "Autarky"
DSM_proportion = "high_DSM"
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

# Daemons
price_managing_daemons = create_daemons(natures, sizing)

# Contracts
contracts = create_contracts(natures, price_managing_daemons)

# Aggregators
aggregators = create_aggregators(natures, strategies)

# Agents
agents = create_agents()

# Devices
create_devices(world, aggregators, contracts, agents, price_managing_daemons, DSM_proportion, sizing)

# Dataloggers
create_dataloggers()

# ##############################################################################################
# Simulation
# ##############################################################################################
world.start()



