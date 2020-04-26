# first run for SFT 2020
# Exchange strategy: Autarky
# Distribution strategy: Partial
# Contract: 67 Normal, 20 DLC, 13 Curtailment


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.SFT_2020.CaseBuildingBlocks import *

# parameters
exchange_strategy = "Autarky"
distribution_strategy = "Partial"
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

# Daemons
price_managing_daemons = create_daemons(natures)

# Contracts
contracts = create_contracts(natures, price_managing_daemons)

# Aggregators
aggregators = create_aggregators(natures, strategies)

# Agents
agents = create_agents()

# Devices
create_devices(world, aggregators, contracts, agents, price_managing_daemons, DSM_proportion)

# Dataloggers
create_dataloggers()


# ##############################################################################################
# Simulation
# ##############################################################################################
world.start()



