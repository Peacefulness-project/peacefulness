# This script checks that the flexibility works well for contracts

# ##############################################################################################
# Importations
from datetime import datetime

from os import chdir

from lib.DefaultNatures.DefaultNatures import *

from src.common.Agent import Agent
from src.common.Aggregator import Aggregator
from src.common.Datalogger import Datalogger
from src.common.Nature import Nature
from src.common.World import World

from src.tools.GraphAndTex import graph_options
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
world.set_directory("cases/ValidationCases/Results/ContractsFlexibility")  # here, you have to put the path to your results directory


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
price_manager_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices", {"nature": LVE.name, "buying_price": 0, "selling_price": 0})  # sets prices for flat rate

subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 1, "limit_selling_price": -1})  # sets prices for the system operator


# ##############################################################################################
# Creation of strategies
# the different distribution strategies
strategy_elec = subclasses_dictionary["Strategy"]["LightAutarkyEmergency"]()

# strategy grid, which always proposes an infinite quantity to sell and to buy
grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()


# ##############################################################################################
# Manual creation of agents
BAU_owner = Agent("BAU_owner")
cooperative_owner = Agent("cooperative_owner")
curtailment_owner = Agent("curtailment_owner")

aggregators_manager = Agent("aggregators_manager")


# ##############################################################################################
# Manual creation of contracts
BAU_elec_contract = subclasses_dictionary["Contract"]["EgoistContract"]("elec_contract", LVE, price_manager_elec)

cooperative_elec_contract = subclasses_dictionary["Contract"]["CooperativeContract"]("cooperative_elec_contract", LVE, price_manager_elec)

curtailment_elec_contract = subclasses_dictionary["Contract"]["CurtailmentContract"]("curtailment_elec_contract", LVE, price_manager_elec)

# ##############################################################################################
# Creation of aggregators
aggregator_grid = Aggregator("national_grid", LVE, grid_strategy, aggregators_manager)

aggregator_elec = Aggregator("local_grid", LVE, strategy_elec, aggregators_manager, aggregator_grid, BAU_elec_contract)


# ##############################################################################################
# Manual creation of devices

# Each device is created 3 times
# BAU contract
subclasses_dictionary["Device"]["Dishwasher"]("BAU_dishwasher", BAU_elec_contract, BAU_owner, aggregator_elec, {"user": "dummy_user", "device": "dummy_usage"}, "cases/ValidationCases/AdditionalData/DevicesProfiles/Dishwasher.json")

# Cooperative contract
subclasses_dictionary["Device"]["Dishwasher"]("cooperative_dishwasher", cooperative_elec_contract, cooperative_owner, aggregator_elec, {"user": "dummy_user", "device": "dummy_usage"}, "cases/ValidationCases/AdditionalData/DevicesProfiles/Dishwasher.json")

# Curtailment contract
subclasses_dictionary["Device"]["Dishwasher"]("curtailment_dishwasher", curtailment_elec_contract, curtailment_owner, aggregator_elec, {"user": "dummy_user", "device": "dummy_usage"}, "cases/ValidationCases/AdditionalData/DevicesProfiles/Dishwasher.json")


# ##############################################################################################
# Creation of the validation daemon
description = "This script checks that the flexibility works well for contracts."

filename = "contracts_flexibility_validation"

reference_values = {"BAU_owner.LVE.energy_bought": [0, 0, 0, 0, 0, 0, 0, 0, 0.5, 0.4, 0.2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "cooperative_owner.LVE.energy_bought": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5, 0.4, 0.2, 0, 0, 0, 0, 0],
                    "curtailment_owner.LVE.energy_bought": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    }

name = "Bought_Energy_BAU"
export_plot1 = {
    "name": name,
    "filename": "export_"+name,
    "options": graph_options(["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{P} \, [\si{\watt}]$",
          "graphs": [ {"catalog_name_entry": "BAU_owner.LVE.energy_bought_reference", "style": "points", "legend": r"ref."},
                      {"catalog_name_entry": "BAU_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r"num."} ]
          }
}

name = "Bought_Energy_CooperativeContract"
export_plot2 = {
    "name": name,
    "filename": "export_"+name,
    "options": graph_options(["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{P} \, [\si{\watt}]$",
          "graphs": [ {"catalog_name_entry": "cooperative_owner.LVE.energy_bought_reference", "style": "points", "legend": r"ref."},
                      {"catalog_name_entry": "cooperative_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r"num."} ]
          }
}

name = "Bought_Energy_CurtailmentContract"
export_plot3 = {
    "name": name,
    "filename": "export_"+name,
    "options": graph_options(["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{P} \, [\si{\watt}]$",
          "graphs": [ {"catalog_name_entry": "curtailment_owner.LVE.energy_bought_reference", "style": "points", "legend": r"ref."},
                      {"catalog_name_entry": "curtailment_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r"num"},
                      ]
          }
}

name = "Bought_Energy_Alltogether"
export_plot4 = {
    "name": name,
    "filename": "export_"+name,
    "options": graph_options(["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{P}_{ref.} \, [\si{\watt}]$",
          "graphs": [ {"catalog_name_entry": "BAU_owner.LVE.energy_bought_reference", "style": "points", "legend": r"BAU"},
                      {"catalog_name_entry": "cooperative_owner.LVE.energy_bought_reference", "style": "points", "legend": r"coop."},
                      {"catalog_name_entry": "curtailment_owner.LVE.energy_bought_reference", "style": "points", "legend": r"curt."}
                      ]
          },
    "Y2": {"label": r"$\mathcal{P}_{num.} \, [\si{\watt}]$",
          "graphs": [ {"catalog_name_entry": "BAU_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""},
                      {"catalog_name_entry": "cooperative_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""},
                      {"catalog_name_entry": "curtailment_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""}
                      ]
          }
}

parameters = {"description": description, "filename": filename, "reference_values": reference_values, "tolerance": 1E-6, "export_plots": [export_plot1, export_plot2, export_plot3, export_plot4]}

validation_daemon = subclasses_dictionary["Daemon"]["ValidationDaemon"]("contracts_flexibility_test", parameters)


# ##############################################################################################
# Simulation start
world.start()



