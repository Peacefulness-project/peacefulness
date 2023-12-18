# This script checks that the billing works well for contracts

# ##############################################################################################
# Importations
from datetime import datetime


from lib.DefaultNatures.DefaultNatures import *

from src.common.Agent import Agent
from src.common.Aggregator import Aggregator
from src.common.Strategy import *
from src.common.World import World

from src.tools.GraphAndTex import GraphOptions
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
world.set_directory("cases/ValidationCases/Results/ContractsTariffs")  # here, you have to put the path to your results directory


# ##############################################################################################
# Definition of the random seed
# The default seed is the current time (the value returned by datetime.now())
world.set_random_seed("seed")


# ##############################################################################################
# Time parameters
# it needs a start date, the value of an iteration in hours and the total number of iterations
start_date = datetime(year=2000, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)  # a start date in the datetime format
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
price_manager_elec_flat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices", {"nature": LVE.name, "buying_price": 0.1, "selling_price": 0})  # sets prices for flat rate
price_manager_elec_TOU = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("TOU_prices", {"nature": LVE.name, "buying_price": [0.1, 0.2], "selling_price": [0, 0], "on-peak_hours": [[6, 22]]})  # sets prices for flat rate
price_manager_elec_RTP = subclasses_dictionary["Daemon"]["PriceManagerRTPDaemon"]("RTP_prices", {"nature": LVE.name, "location":"France"})  # sets prices for RTP rate

subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0.2, "limit_selling_price": -1})  # sets prices for the system operator

# ##############################################################################################
# Creation of strategies
# the different distribution strategies
strategy_elec = subclasses_dictionary["Strategy"]["LightAutarkyFullButFew"](get_emergency)

# strategy grid, which always proposes an infinite quantity to sell and to buy
grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()


# ##############################################################################################
# Manual creation of agents
flat_owner = Agent("flat_owner")
TOU_owner = Agent("TOU_owner")
RTP_owner = Agent("RTP_owner")

aggregators_manager = Agent("aggregators_manager")


# ##############################################################################################
# Manual creation of contracts
flat_elec_contract = subclasses_dictionary["Contract"]["EgoistContract"]("flat_elec_contract", LVE, price_manager_elec_flat)

TOU_elec_contract = subclasses_dictionary["Contract"]["EgoistContract"]("TOU_elec_contract", LVE, price_manager_elec_TOU)

RTP_elec_contract = subclasses_dictionary["Contract"]["EgoistContract"]("RTP_elec_contract", LVE, price_manager_elec_RTP)


# ##############################################################################################
# Creation of aggregators
aggregator_grid = Aggregator("national_grid", LVE, grid_strategy, aggregators_manager)

aggregator_elec = Aggregator("local_grid", LVE, strategy_elec, aggregators_manager, aggregator_grid, flat_elec_contract)


# ##############################################################################################
# Manual creation of devices

# Each device is created 3 times
# flat contract
subclasses_dictionary["Device"]["Background"]("flat_device", flat_elec_contract, flat_owner, aggregator_elec, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")

# TOU contract
subclasses_dictionary["Device"]["Background"]("TOU_device", TOU_elec_contract, TOU_owner, aggregator_elec, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")

# RTP contract
subclasses_dictionary["Device"]["Background"]("RTP_device", RTP_elec_contract, RTP_owner, aggregator_elec, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")


# ##############################################################################################
# Creation of the validation daemon
description = "This script checks that the billing works well for contracts."

filename = "contracts_tariffs_validation"

reference_values = {"flat_owner.money_spent": [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3],
                    "TOU_owner.money_spent": [0, 0.1, 0.2, 0.3, 0.4, 0.5, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0, 4.2, 2.2, 2.3],
                    "RTP_owner.money_spent": [0, 0.1703*1, 0.155*2, 0.1402*3, 0.0855*4, 0.0684*5, 0.0669*6, 0.0873*7, 0.1524*8, 0.1306*9, 0.1332*10, 0.1261*11, 0.1441*12, 0.1454*13, 0.1214*14, 0.1234*15, 0.1166*16, 0.1205*17, 0.179*18, 0.2*19, 0.2*20, 0.2*21, 0.2*22, 0.2*23]
                    }

name = "Spent_Money_FLAT"
export_plot1 = {
    "name": name,
    "filename": "export_"+name,
    "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{C} \, [$\euro{}$]$",
          "graphs": [ {"catalog_name_entry": "flat_owner.money_spent_reference", "style": "points", "legend": r"ref."},
                      {"catalog_name_entry": "flat_owner.money_spent_simulation", "style": "lines", "legend": r"num."} ]
          }
}

name = "Spent_Money_TOU"
export_plot2 = {
    "name": name,
    "filename": "export_"+name,
    "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{C} \, [$\euro{}$]$",
          "graphs": [ {"catalog_name_entry": "TOU_owner.money_spent_reference", "style": "points", "legend": r"ref."},
                      {"catalog_name_entry": "TOU_owner.money_spent_simulation", "style": "lines", "legend": r"num."} ]
          }
}

name = "Spent_Money_RTP"
export_plot3 = {
    "name": name,
    "filename": "export_"+name,
    "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{C} \, [$\euro{}$]$",
          "graphs": [ {"catalog_name_entry": "RTP_owner.money_spent_reference", "style": "points", "legend": r"ref."},
                      {"catalog_name_entry": "RTP_owner.money_spent_simulation", "style": "lines", "legend": r"num"},
                      ]
          }
}

name = "Spent_Money_Alltogether"
export_plot4 = {
    "name": name,
    "filename": "export_"+name,
    "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{C}_{ref.} \, [$\euro{}$]$",
          "graphs": [ {"catalog_name_entry": "flat_owner.money_spent_reference", "style": "points", "legend": r"flat"},
                      {"catalog_name_entry": "TOU_owner.money_spent_reference", "style": "points", "legend": r"TOU"},
                      {"catalog_name_entry": "RTP_owner.money_spent_reference", "style": "points", "legend": r"RTP"}
                      ]
          },
    "Y2": {"label": r"$\mathcal{C}_{num.} \, [$\euro{}$]$",
          "graphs": [ {"catalog_name_entry": "flat_owner.money_spent_simulation", "style": "lines", "legend": r""},
                      {"catalog_name_entry": "TOU_owner.money_spent_simulation", "style": "lines", "legend": r""},
                      {"catalog_name_entry": "RTP_owner.money_spent_simulation", "style": "lines", "legend": r""}
                      ]
          }
}

parameters = {"description": description, "filename": filename, "reference_values": reference_values, "tolerance": 1E-6, "export_plots": [export_plot1, export_plot2, export_plot3, export_plot4]}

validation_daemon = subclasses_dictionary["Daemon"]["ValidationDaemon"]("contracts_tariffs_test", parameters)


# ##############################################################################################
# Simulation start
world.start()



