# This script check that aggregators do not make a difference between devices and sub-aggregators

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
world.set_directory("cases/ValidationCases/Results/Subaggregators")  # here, you have to put the path to your results directory


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

subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0, "limit_selling_price": 0})  # sets prices for the system operator

# ##############################################################################################
# Creation of strategies
# BAU strategy
strategy_elec = subclasses_dictionary["Strategy"]["LightAutarkyEmergency"]()

# strategy grid, which always proposes an infinite quantity to sell and to buy
grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()


# ##############################################################################################
# Manual creation of agents
devices_owner_sup = Agent("device_owner_sup")

devices_owner_inf = Agent("device_owner_inf")

aggregator_sup_manager = Agent("aggregators_sup_manager")

aggregator_inf_manager = Agent("aggregators_inf_manager")


# ##############################################################################################
# Manual creation of contracts
BAU_elec = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_elec", LVE, price_manager_elec)

curtailment_elec = subclasses_dictionary["Contract"]["CurtailmentContract"]("curtailment_elec", LVE, price_manager_elec)


# ##############################################################################################
# Creation of aggregators
aggregator_grid = Aggregator("national_grid", LVE, grid_strategy, aggregator_sup_manager)

aggregator_elec_sup = Aggregator("local_grid_superior", LVE, strategy_elec, aggregator_sup_manager, aggregator_grid, BAU_elec)

aggregator_elec_inf = Aggregator("local_grid_inferior", LVE, strategy_elec, aggregator_inf_manager, aggregator_elec_sup, BAU_elec)


# ##############################################################################################
# Manual creation of devices

# aggregator sup
device_sup_served = subclasses_dictionary["Device"]["Background"]("device_sup_served", BAU_elec, devices_owner_sup, aggregator_elec_sup, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")
device_sup_not_served = subclasses_dictionary["Device"]["Background"]("device_sup_not_served", curtailment_elec, devices_owner_sup, aggregator_elec_sup, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")

# aggregator_inf
device_inf_served = subclasses_dictionary["Device"]["Background"]("device_inf_served", BAU_elec, devices_owner_inf, aggregator_elec_inf, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")
device_inf_not_served = subclasses_dictionary["Device"]["Background"]("device_inf_not_served", curtailment_elec, devices_owner_inf, aggregator_elec_inf, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")


# ##############################################################################################
# Creation of the validation daemon
description = "This script check that aggregators do not make a difference between devices and sub-aggregators"

filename = "subaggregators_validation"

reference_values = {"device_owner_sup.LVE.energy_bought": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
                    "device_owner_inf.LVE.energy_bought": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
                    "aggregators_sup_manager.LVE.energy_bought": [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46],
                    "aggregators_inf_manager.LVE.energy_bought": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
                    }

name = "LVE_sup_balances"
export_plot1 = {
    "name": name,
    "filename": "export_"+name,
    "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{P} \, [\si{\watt}]$",
          "graphs": [{"catalog_name_entry": "device_owner_sup.LVE.energy_bought_reference", "style": "points", "legend": r"ref."},
                      {"catalog_name_entry": "device_owner_sup.LVE.energy_bought_simulation", "style": "lines", "legend": r"num."}]
          }
}

name = "LVE_inf_balances"
export_plot2 = {
    "name": name,
    "filename": "export_"+name,
    "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{P} \, [\si{\watt}]$",
          "graphs": [{"catalog_name_entry": "device_owner_inf.LVE.energy_bought_reference", "style": "points", "legend": r"ref."},
                      {"catalog_name_entry": "device_owner_inf.LVE.energy_bought_simulation", "style": "lines", "legend": r"num."}]
          }
}

parameters = {"description": description, "reference_values": reference_values, "filename": filename, "tolerance": 1E-6, "export_plots": [export_plot1, export_plot2]}

validation_daemon = subclasses_dictionary["Daemon"]["ValidationDaemon"]("subaggregators_test", parameters)


# ##############################################################################################
# Simulation start
world.start()



