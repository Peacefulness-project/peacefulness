# first run for SFT 2020
# Exchange strategy: Autarky
# Distribution strategy: Emergency
# Contract: 67 Normal, 20 DLC, 13 Curtailment


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.SFT_2020.CaseBuildingBlocks import *

# parameters
exchange_strategy = "Autarky"
distribution_strategy = "Revenues"
DSM_proportion = "low_DSM"

# Importation of subclasses
subclasses_dictionary = get_subclasses()

# world and parameters
world = create_world_with_set_parameters(exchange_strategy, distribution_strategy, DSM_proportion)


# ##############################################################################################
# Model creation
# ##############################################################################################
# Strategies
strategies = create_strategies(exchange_strategy, distribution_strategy)

# Natures
natures = create_natures()

# Contracts
[contracts, price_IDs] = create_contracts(natures)

# Aggregators
aggregators = create_aggregators(natures, strategies)

# Agents
agents = create_agents()

# Devices
create_devices(world, aggregators, contracts, agents, price_IDs, DSM_proportion)

# Daemons
create_daemons(natures, price_IDs)

# Dataloggers
create_dataloggers()

# ##############################################################################################
# Simulation
# ##############################################################################################
world.start()



