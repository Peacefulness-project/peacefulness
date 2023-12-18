# This script checks that the user profiles work well

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
world.set_directory("cases/ValidationCases/Results/UserProfiles")  # here, you have to put the path to your results directory


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
price_manager_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices", {"nature": LVE.name, "buying_price": 0, "selling_price": 0})  # sets prices for flat rate

subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 1, "limit_selling_price": 1})  # sets prices for the system operator

# Water temperature
# this daemon is responsible for the value of the water temperature in the catalog
water_temperature_daemon = subclasses_dictionary["Daemon"]["ColdWaterTemperatureDaemon"]({"location": "Pau"}, "cases/ValidationCases/AdditionalData/Meteo/ColdWaterTemperatureProfiles.json")

# Indoor temperature
# this daemon is responsible for the value of indoor temperatures in the catalog
indoor_temperature_daemon = subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

# Outdoor temperature
# this daemon is responsible for the value of outside temperature in the catalog
outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Pau"})

# ##############################################################################################
# Creation of strategies
# the different distribution strategies
strategy = subclasses_dictionary["Strategy"]["AlwaysSatisfied"]()


# strategy grid, which always proposes an infinite quantity to sell and to buy
grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()


# ##############################################################################################
# Manual creation of agents

# hot water tank owners
early_hot_water_tank_owner = Agent("early_hot_water_tank_owner")
month_dependency_hot_water_tank_owner = Agent("month_dependency_hot_water_tank_owner")
short_period_hot_water_tank_owner = Agent("short_period_hot_water_tank_owner")
two_usages_hot_water_tank_owner = Agent("two_usages_hot_water_tank_owner")

# heatings owners
early_heating_owner = Agent("early_heating_owner")
hot_heating_owner = Agent("hot_heating_owner")
short_usage_heating_owner = Agent("short_usage_heating_owner")

aggregators_manager = Agent("aggregators_manager")


# ##############################################################################################
# Manual creation of contracts
elec_contract = subclasses_dictionary["Contract"]["EgoistContract"]("elec_contract", LVE, price_manager_elec)


# ##############################################################################################
# Creation of aggregators
aggregator_grid = Aggregator("national_grid", LVE, grid_strategy, aggregators_manager)

local_aggregator = Aggregator("local_grid_emergency", LVE, strategy, aggregators_manager, aggregator_grid, elec_contract)


# ##############################################################################################
# Manual creation of devices

# hot water tanks
subclasses_dictionary["Device"]["HotWaterTank"]("hot_water_tank_early", elec_contract, early_hot_water_tank_owner, local_aggregator, {"user": "dummy_user_early", "device": "dummy_usage"}, {"cold_water_temperature_daemon": water_temperature_daemon.name}, "cases/ValidationCases/AdditionalData/DevicesProfiles/HotWaterTank.json")
subclasses_dictionary["Device"]["HotWaterTank"]("hot_water_tank_month_dependency", elec_contract, month_dependency_hot_water_tank_owner, local_aggregator, {"user":"dummy_user_month_dependency", "device": "dummy_usage"}, {"cold_water_temperature_daemon": water_temperature_daemon.name}, "cases/ValidationCases/AdditionalData/DevicesProfiles/HotWaterTank.json")
subclasses_dictionary["Device"]["HotWaterTank"]("hot_water_tank_short_period", elec_contract, short_period_hot_water_tank_owner, local_aggregator, {"user": "dummy_user_short_period", "device": "dummy_usage"}, {"cold_water_temperature_daemon": water_temperature_daemon.name}, "cases/ValidationCases/AdditionalData/DevicesProfiles/HotWaterTank.json")
subclasses_dictionary["Device"]["HotWaterTank"]("hot_water_tank_2_usages", elec_contract, two_usages_hot_water_tank_owner, local_aggregator, {"user": "dummy_user_2_usages", "device": "dummy_usage"}, {"cold_water_temperature_daemon": water_temperature_daemon.name}, "cases/ValidationCases/AdditionalData/DevicesProfiles/HotWaterTank.json")

# heatings
subclasses_dictionary["Device"]["Heating"]("heating_early", elec_contract, early_heating_owner, local_aggregator, {"user": "dummy_user_early", "device": "dummy_elec"}, {"outdoor_temperature_daemon": outdoor_temperature_daemon.name}, "cases/ValidationCases/AdditionalData/DevicesProfiles/Heating.json")
subclasses_dictionary["Device"]["Heating"]("heating_hot", elec_contract, hot_heating_owner, local_aggregator, {"user": "dummy_user_hot", "device": "dummy_elec"}, {"outdoor_temperature_daemon": outdoor_temperature_daemon.name}, "cases/ValidationCases/AdditionalData/DevicesProfiles/Heating.json")
subclasses_dictionary["Device"]["Heating"]("heating_short_usage", elec_contract, short_usage_heating_owner, local_aggregator, {"user": "dummy_user_short_usage", "device": "dummy_elec"}, {"outdoor_temperature_daemon": outdoor_temperature_daemon.name}, "cases/ValidationCases/AdditionalData/DevicesProfiles/Heating.json")


# ##############################################################################################
# Creation of the validation daemon
description = "This script checks that the user profiles work well"

filename = "user_profiles_validation"

reference_values = {"early_hot_water_tank_owner.LVE.energy_bought": [418/3.6/10000, 0, 0, 0, 0, 0, 0, 418/3.6/10000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "month_dependency_hot_water_tank_owner.LVE.energy_bought": [418/3.6/10000*2, 0, 0, 0, 0, 0, 0, 0, 418/3.6/10000*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "short_period_hot_water_tank_owner.LVE.energy_bought": [418/3.6/10000, 0, 0, 0, 0, 0, 0, 0, 418/3.6/10000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 418/3.6/10000, 0, 0, 0],
                    "two_usages_hot_water_tank_owner.LVE.energy_bought": [418/3.6/10000/2, 0, 0, 0, 0, 0, 0, 0, 418/3.6/10000/2, 0, 0, 0, 0, 0, 0, 0, 418/3.6/10000/2, 0, 0, 0, 0, 0, 0, 0],

                    "early_heating_owner.LVE.energy_bought": [0, 0, 0, 0, 15.4, 15.5, 15.6, 15.8, 15.2, 14.7, 5.2, 3.9, 2.7, 1.4, 1.3, 1.1, 0.9, 1.8, 2.7, 0, 0, 0, 0, 0],
                    "hot_heating_owner.LVE.energy_bought": [0, 0, 0, 0, 0, 17.5, 17.6, 17.8, 17.2, 16.7, 16.2, 5.9, 4.7, 3.4, 3.3, 3.1, 2.9, 3.8, 4.7, 5.6, 0, 0, 0, 0],
                    "short_usage_heating_owner.LVE.energy_bought": [0, 0, 0, 0, 0, 15.5, 15.6, 15.8, 15.2, 14.7, 5.2, 3.9, 2.7, 1.4, 1.3, 1.1, 0.9, 1.8, 2.7, 0, 0, 0, 0, 0]
                    }

name = "DHW_early_balances"
export_plot1 = {
    "name": name,
    "filename": "export_"+name,
    "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{P} \, [\si{\watt}]$",
          "graphs": [ {"catalog_name_entry": "early_hot_water_tank_owner.LVE.energy_bought_reference", "style": "points", "legend": r"ref."},
                      {"catalog_name_entry": "early_hot_water_tank_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r"num."} ]
          }
}

name = "DHW_monthly_balances"
export_plot2 = {
    "name": name,
    "filename": "export_"+name,
    "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{P} \, [\si{\watt}]$",
          "graphs": [ {"catalog_name_entry": "month_dependency_hot_water_tank_owner.LVE.energy_bought_reference", "style": "points", "legend": r"ref."},
                      {"catalog_name_entry": "month_dependency_hot_water_tank_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r"num."} ]
          }
}

name = "DHW_short_period_balances"
export_plot3= {
    "name": name,
    "filename": "export_"+name,
    "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{P} \, [\si{\watt}]$",
          "graphs": [ {"catalog_name_entry": "short_period_hot_water_tank_owner.LVE.energy_bought_reference", "style": "points", "legend": r"ref."},
                      {"catalog_name_entry": "short_period_hot_water_tank_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r"num."} ]
          }
}

name = "DHW_two_usages_balances"
export_plot4 = {
    "name": name,
    "filename": "export_"+name,
    "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{P} \, [\si{\watt}]$",
          "graphs": [ {"catalog_name_entry": "two_usages_hot_water_tank_owner.LVE.energy_bought_reference", "style": "points", "legend": r"ref."},
                      {"catalog_name_entry": "two_usages_hot_water_tank_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r"num."} ]
          }
}

name = "DHW_Alltogether_balances"
export_plot5 = {
    "name": name,
    "filename": "export_"+name,
    "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{P}_{ref.} \, [\si{\watt}]$",
          "graphs": [ {"catalog_name_entry": "early_hot_water_tank_owner.LVE.energy_bought_reference", "style": "points", "legend": r"early"},
                      {"catalog_name_entry": "month_dependency_hot_water_tank_owner.LVE.energy_bought_reference", "style": "points", "legend": r"monthly"},
                      {"catalog_name_entry": "short_period_hot_water_tank_owner.LVE.energy_bought_reference", "style": "points", "legend": r"short"},
                      {"catalog_name_entry": "two_usages_hot_water_tank_owner.LVE.energy_bought_reference", "style": "points", "legend": r"2 usages"}
                      ]
          },
    "Y2": {"label": r"$\mathcal{P}_{num.} \, [\si{\watt}]$",
          "graphs": [{"catalog_name_entry": "early_hot_water_tank_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""},
                     {"catalog_name_entry": "month_dependency_hot_water_tank_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""},
                     {"catalog_name_entry": "short_period_hot_water_tank_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""},
                     {"catalog_name_entry": "two_usages_hot_water_tank_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""}
                     ]
          }
}

name = "Heating_early_balances"
export_plot6 = {
    "name": name,
    "filename": "export_"+name,
    "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{P} \, [\si{\watt}]$",
          "graphs": [ {"catalog_name_entry": "early_heating_owner.LVE.energy_bought_reference", "style": "points", "legend": r"ref."},
                      {"catalog_name_entry": "early_heating_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r"num."} ]
          }
}

name = "Heating_monthly_balances"
export_plot7 = {
    "name": name,
    "filename": "export_"+name,
    "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{P} \, [\si{\watt}]$",
          "graphs": [ {"catalog_name_entry": "hot_heating_owner.LVE.energy_bought_reference", "style": "points", "legend": r"ref."},
                      {"catalog_name_entry": "hot_heating_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r"num."} ]
          }
}

name = "Heating_short_period_balances"
export_plot8= {
    "name": name,
    "filename": "export_"+name,
    "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{P} \, [\si{\watt}]$",
          "graphs": [ {"catalog_name_entry": "short_usage_heating_owner.LVE.energy_bought_reference", "style": "points", "legend": r"ref."},
                      {"catalog_name_entry": "short_usage_heating_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r"num."} ]
          }
}


name = "Heating_Alltogether_balances"
export_plot9 = {
    "name": name,
    "filename": "export_"+name,
    "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{P}_{ref.} \, [\si{\watt}]$",
          "graphs": [ {"catalog_name_entry": "early_heating_owner.LVE.energy_bought_reference", "style": "points", "legend": r"early"},
                      {"catalog_name_entry": "hot_heating_owner.LVE.energy_bought_reference", "style": "points", "legend": r"hot"},
                      {"catalog_name_entry": "short_usage_heating_owner.LVE.energy_bought_reference", "style": "points", "legend": r"short"}
                      ]
          },
    "Y2": {"label": r"$\mathcal{P}_{num.} \, [\si{\watt}]$",
          "graphs": [{"catalog_name_entry": "early_heating_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""},
                     {"catalog_name_entry": "hot_heating_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""},
                     {"catalog_name_entry": "short_usage_heating_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""}
                     ]
          }
}

parameters = {"description": description, "reference_values": reference_values, "filename": filename, "tolerance": 1E-6, "export_plots": [export_plot1, export_plot2, export_plot3, export_plot4, export_plot5, export_plot6, export_plot7, export_plot8, export_plot9]}

validation_daemon = subclasses_dictionary["Daemon"]["ValidationDaemon"]("user_profiles_test", parameters)


# ##############################################################################################
# Simulation start
world.start()



