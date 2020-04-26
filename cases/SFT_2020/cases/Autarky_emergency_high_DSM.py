# Exchange strategy: Autarky
# Distribution strategy: Emergency
# Contract: 33 Normal, 40 DLC, 27 Curtailment


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.SFT_2020.CaseBuildingBlocks import *

# parameters
exchange_strategy = "Autarky"
distribution_strategy = "Emergency"
DSM_proportion = "high_DSM"

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



