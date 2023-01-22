# This script checks the complex contracts

# ##############################################################################################
# Importations
from datetime import datetime

from lib.DefaultNatures.DefaultNatures import *

from src.common.Agent import Agent
from src.common.Aggregator import Aggregator
from src.common.Strategy import *
from src.common.World import World

from src.tools.SubclassesDictionary import get_subclasses


# ##############################################################################################
# Minimum
# the following objects are necessary for the simulation to be performed
# you need exactly one object of each type
# ##############################################################################################

# ##############################################################################################
# Importation of subclasses
# all the subclasses are imported in the following dictionary
subclasses_dictionary = get_subclasses()

# ##############################################################################################
# Creation of the world
# a world contains all the other elements of the model
# a world needs just a name
name_world = "validation"
world = World(name_world)  # creation


# ##############################################################################################
# Definition of the path to the files
world.set_directory("cases/ValidationCases/Results/ComplexContracts")  # here, you have to put the path to your results directory


# ##############################################################################################
# Definition of the random seed
# The default seed is the current time (the value returned by datetime.now())
world.set_random_seed("seed")


# ##############################################################################################
# Time parameters
# it needs a start date, the value of an iteration in hours and the total number of iterations
start_date = datetime(year=1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)  # a start date in the datetime format
world.set_time(start_date,  # time management: start date
               1,  # value of a time step (in hours)
               24)  # number of time steps simulated


# ##############################################################################################
# Model
# ##############################################################################################

# ##############################################################################################
# Creation of nature
# low voltage electricity
LVE = load_low_voltage_electricity()


# ##############################################################################################
# Creation of daemons
price_manager_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices", {"nature": LVE.name, "buying_price": 0.2, "selling_price": 0})  # sets prices for flat rate

subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 1, "limit_selling_price": -1})  # sets prices for the system operator


# ##############################################################################################
# Creation of strategies
# the different distribution strategies
Autarky_strategy = subclasses_dictionary["Strategy"]["AutarkyFullButFew"](get_emergency)

# strategy grid, which always proposes an infinite quantity to sell and to buy
grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()


# ##############################################################################################
# Manual creation of agents
curtailment_ramp_owner = Agent("curtailment_ramp_owner")

prod_owner = Agent("prod_owner")

aggregators_manager = Agent("aggregators_manager")


# ##############################################################################################
# Manual creation of contracts
BAU_elec_contract = subclasses_dictionary["Contract"]["EgoistContract"]("elec_contract", LVE, price_manager_elec)

# curtailment ramp contract test
curtailment_ramp_elec_contract_no_degradation = subclasses_dictionary["Contract"]["CurtailmentRampContract"]("curtailment_ramp_no_degradation", LVE, price_manager_elec, {"bonus": 0.1, "depreciation_time": inf, "depreciation_residual": 0.01})
curtailment_ramp_elec_contract_degradation = subclasses_dictionary["Contract"]["CurtailmentRampContract"]("curtailment_ramp_degradation", LVE, price_manager_elec, {"bonus": 0.1, "depreciation_time": 1, "depreciation_residual": 0.9})
curtailment_elec_contract = subclasses_dictionary["Contract"]["CurtailmentContract"]("curtailment_elec_contract", LVE, price_manager_elec)


# ##############################################################################################
# Creation of aggregators
aggregator_grid = Aggregator("national_grid", LVE, grid_strategy, aggregators_manager)

# curtailment ramp test
aggregator_elec_curtailment_ramp_no_degradation = Aggregator("aggregator_elec_curtailment_ramp_no_degradation", LVE, Autarky_strategy, aggregators_manager, aggregator_grid, BAU_elec_contract)
aggregator_elec_curtailment_ramp_degradation = Aggregator("aggregator_elec_curtailment_ramp_degradation", LVE, Autarky_strategy, aggregators_manager, aggregator_grid, BAU_elec_contract)


# ##############################################################################################
# Manual creation of devices

# Curtailment ramp contract
# no degradation of effort along the time
subclasses_dictionary["Device"]["Background"]("curtailment_ramp_device_no_degradation", curtailment_ramp_elec_contract_no_degradation, curtailment_ramp_owner, aggregator_elec_curtailment_ramp_no_degradation, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")
subclasses_dictionary["Device"]["Background"]("curtailment_ramp_device_production", curtailment_elec_contract, curtailment_ramp_owner, aggregator_elec_curtailment_ramp_no_degradation, {"user": "dummy_user", "device": "production_complex_contracts_test"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")

# degradation of effort along the time
subclasses_dictionary["Device"]["Background"]("curtailment_ramp_device_degradation", curtailment_ramp_elec_contract_degradation, curtailment_ramp_owner, aggregator_elec_curtailment_ramp_degradation, {"user": "dummy_user", "device": "constant_consumption"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")

# ##############################################################################################
# Creation of the validation daemon
description = "This script checks the complex contracts."

filename = "complex_contracts_validation"

reference_values = {"curtailment_ramp_no_degradation.money_spent": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2.4, 2.6, 2.8, 3, 3.2, 3.4, 3.6, 3.6, 3.6, 3.6, 3.6, 3.6],
                    "curtailment_ramp_no_degradation.money_earned": [0, 0.1, 0.4, 0.9, 1.6, 2.5, 3.6, 4.9, 6.4, 8.1, 10, 11, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5],

                    "curtailment_ramp_degradation.money_earned": [0.1, 0.19, 0.271, 0.3439, 0.40951, 0.46855899999999995, 0.5217031, 0.56953279, 0.612579511, 0.651321599, 0.68618940391, 0.717570463519, 0.7458134171671, 0.77123207545039, 0.7941088679053511, 0.8146979811148161, 0.8332281830033346, 0.849905364703, 0.8649148282327008, 0.8784233454094308, 0.8905810108684877, 0.901522909781639, 0.9113706188034751, 0.9202335569231277]
                    }

# name = "Bought_Energy_BAU"
# export_plot1 = {
#     "name": name,
#     "filename": "export_"+name,
#     "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
#     "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
#     "Y": {"label": r"$\mathcal{P} \, [\si{\watt}]$",
#           "graphs": [ {"catalog_name_entry": "BAU_owner.LVE.energy_bought_reference", "style": "points", "legend": r"ref."},
#                       {"catalog_name_entry": "BAU_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r"num."} ]
#           }
# }

parameters = {"description": description, "filename": filename, "reference_values": reference_values, "tolerance": 1E-6, "export_plots": []}

validation_daemon = subclasses_dictionary["Daemon"]["ValidationDaemon"]("complex_contracts_test", parameters)


# ##############################################################################################
# Simulation start
world.start()



