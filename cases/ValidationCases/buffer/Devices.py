# This script checks that devices are working well.

# ##############################################################################################
# Importations
from datetime import datetime

from os import chdir

from src.common.World import World

from src.common.Nature import Nature
from lib.DefaultNatures.DefaultNatures import *

from src.common.Agent import Agent

from src.common.Aggregator import Aggregator

from src.common.Datalogger import Datalogger

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
world.set_directory("cases/ValidationCases/Results/Devices")  # here, you have to put the path to your results directory


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
# Creation of strategies

# BAU strategy
BAU_strategy = subclasses_dictionary["Strategy"]["AlwaysSatisfied"]()

# strategy grid, which always proposes an infinite quantity to sell and to buy
grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()


# ##############################################################################################
# Creation of nature
# low voltage electricity
LVE = load_low_voltage_electricity()


# ##############################################################################################
# Creation of daemons
price_manager_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_elec", {"nature": LVE.name, "buying_price": 0, "selling_price": 0})  # sets prices for flat rate

subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 1, "limit_selling_price": -1})  # sets prices for the system operator


# Indoor temperature
# this daemon is responsible for the value of indoor temperatures in the catalog
indoor_temperature_daemon = subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

# Outdoor temperature
# this daemon is responsible for the value of outside temperature in the catalog
outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Pau"})

# Water temperature
# this daemon is responsible for the value of the water temperature in the catalog
water_temperature_daemon = subclasses_dictionary["Daemon"]["ColdWaterDaemon"]({"location": "Pau", "datafile": "cases/ValidationCases/AdditionalData/Meteo/ColdWaterTemperatureProfiles.json"})

# Irradiation
# this daemon is responsible for updating the value of raw solar irradiation
irradiation_daemon = subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Pau"})

# Wind
# this daemon is responsible for updating the value of raw solar Wind
wind_daemon = subclasses_dictionary["Daemon"]["WindDaemon"]({"location": "Pau", "datafile": "cases/ValidationCases/AdditionalData/Meteo/WindProfiles.json"})


# ##############################################################################################
# Manual creation of agents
background_owner = Agent("background_owner")
heating_owner = Agent("heating_owner")
dishwasher_owner = Agent("dishwasher_owner")
PV_owner = Agent("PV_owner")
hot_water_tank_owner = Agent("hot_water_tank_owner")
wind_turbine_owner = Agent("wind_turbine_owner")

aggregators_manager = Agent("aggregators_manager")


# ##############################################################################################
# Manual creation of contracts
BAU_contract_elec = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_contract_elec", LVE, price_manager_elec)


# ##############################################################################################
# Creation of aggregators
aggregator_grid = Aggregator("national_grid", LVE, grid_strategy, aggregators_manager)

aggregator_elec = Aggregator("aggregator_elec", LVE, BAU_strategy, aggregators_manager, aggregator_grid, BAU_contract_elec)


# ##############################################################################################
# Manual creation of devices
subclasses_dictionary["Device"]["Background"]("background", BAU_contract_elec, background_owner, aggregator_elec, "dummy_user", "dummy_usage", "cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")
subclasses_dictionary["Device"]["Heating"]("heating", BAU_contract_elec, heating_owner, aggregator_elec, "dummy_user", "dummy_elec", {"location": "Pau"}, "cases/ValidationCases/AdditionalData/DevicesProfiles/Heating.json")
subclasses_dictionary["Device"]["Dishwasher"]("dishwasher", BAU_contract_elec, dishwasher_owner, aggregator_elec, "dummy_user", "dummy_usage", "cases/ValidationCases/AdditionalData/DevicesProfiles/Dishwasher.json")
subclasses_dictionary["Device"]["PV"]("PV", BAU_contract_elec, PV_owner, aggregator_elec, "dummy_user", "dummy_usage", {"location": "Pau", "surface": 1}, "cases/ValidationCases/AdditionalData/DevicesProfiles/PV.json")
subclasses_dictionary["Device"]["HotWaterTank"]("hot_water_tank", BAU_contract_elec, hot_water_tank_owner, aggregator_elec, "dummy_user", "dummy_usage", "cases/ValidationCases/AdditionalData/DevicesProfiles/HotWaterTank.json")
subclasses_dictionary["Device"]["WindTurbine"]("WT", BAU_contract_elec, wind_turbine_owner, aggregator_elec, "dummy_user", "dummy_usage", {"location": "Pau"}, "cases/ValidationCases/AdditionalData/DevicesProfiles/WT.json")


# ##############################################################################################
# Creation of the validation daemon
description = "This script checks that devices are working well."


reference_values = {"background_owner.LVE.energy_bought": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
                    "heating_owner.LVE.energy_bought": [0, 0, 0, 0, 0, 15.4, 15.5, 15.6, 15.8, 15.2, 14.7, 5.2, 3.9, 2.7, 1.4, 1.3, 1.1, 0.9, 1.8, 2.7, 0, 0, 0, 0],
                    "dishwasher_owner.LVE.energy_bought": [0, 0, 0, 0, 0, 0, 0, 0, 0.5, 0.4, 0.2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "PV_owner.LVE.energy_sold": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0.00185, 0.17665, 0.2805, 0.39845, 0.4373, 0.4681, 0.4173, 0.2925, 0.20285, 0, 0, 0, 0, 0, 0, 0],
                    "hot_water_tank_owner.LVE.energy_bought": [418/3.6/10000, 0, 0, 0, 0, 0, 0, 0, 418/3.6/10000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "wind_turbine_owner.LVE.energy_sold": [0.00014625, 0.00014625, 0.00117, 0.003948749999999999, 0.00936, 0.01828125, 0.03158999999999999, 0.05016375, 0.07488, 0.10661625, 0.14625, 0.19465875, 0.25271999999999994, 0.32131125, 0.40131, 0.49359374999999994, 0.59904, 0.71852625, 0.85293, 1.00312875, 1.17, 1.35442125, 1.55727, 1.7794237499999999]
                    }

filename = "devices_validation"

parameters = {"description": description, "reference_values": reference_values, "filename": filename, "tolerance": 1E-6}

validation_daemon = subclasses_dictionary["Daemon"]["ValidationDaemon"]("devices_test", parameters)


# ##############################################################################################
# Simulation start
world.start()






