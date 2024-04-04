# This script checks that devices are working well.

# ##############################################################################################
# Importations
from datetime import datetime


from lib.DefaultNatures.DefaultNatures import *

from src.common.Agent import Agent
from src.common.Aggregator import Aggregator
from src.common.World import World

from src.common.Datalogger import Datalogger
from src.tools.SubclassesDictionary import get_subclasses

from cases.ValidationCases.AdditionalData.DataLoggerRequestsStrategy.DataLoggerRequestsStrategy import DataLoggerRequestsStrategy

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
world.set_directory("cases/ValidationCases/Results/Requests")  # here, you have to put the path to your results directory


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
water_temperature_daemon = subclasses_dictionary["Daemon"]["ColdWaterTemperatureDaemon"]({"location": "Pau"}, "cases/ValidationCases/AdditionalData/Meteo/ColdWaterTemperatureProfiles.json")

# Irradiation
# this daemon is responsible for updating the value of raw solar irradiation
irradiation_daemon = subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Pau"})

# Wind
# this daemon is responsible for updating the value of raw solar Wind
wind_daemon = subclasses_dictionary["Daemon"]["WindSpeedDaemon"]({"location": "Pau"}, "cases/ValidationCases/AdditionalData/Meteo/WindProfiles.json")


# ##############################################################################################
# Creation of strategies

# BAU strategy
BAU_strategy = DataLoggerRequestsStrategy("requests", ["physical_time", "background_owner.LVE.energy_bought"])


# strategy grid, which always proposes an infinite quantity to sell and to buy
grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()


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
subclasses_dictionary["Device"]["Background"]("background", BAU_contract_elec, background_owner, aggregator_elec, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")

subclasses_dictionary["Device"]["Heating"]("heating", BAU_contract_elec, heating_owner, aggregator_elec, {"user": "dummy_user", "device": "dummy_elec"}, {"outdoor_temperature_daemon": outdoor_temperature_daemon.name}, "cases/ValidationCases/AdditionalData/DevicesProfiles/Heating.json")

subclasses_dictionary["Device"]["Dishwasher"]("dishwasher", BAU_contract_elec, dishwasher_owner, aggregator_elec, {"user": "dummy_user", "device": "dummy_usage_devices_test"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Dishwasher.json")

subclasses_dictionary["Device"]["Photovoltaics"]("Photovoltaics", BAU_contract_elec, PV_owner, aggregator_elec, {"device": "dummy_usage"}, {"irradiation_daemon": irradiation_daemon.name, "outdoor_temperature_daemon": outdoor_temperature_daemon.name, "panels": 1}, "cases/ValidationCases/AdditionalData/DevicesProfiles/Photovoltaics.json")

subclasses_dictionary["Device"]["HotWaterTank"]("hot_water_tank", BAU_contract_elec, hot_water_tank_owner, aggregator_elec, {"user": "dummy_user", "device": "dummy_usage_devices_test"}, {"cold_water_temperature_daemon": water_temperature_daemon.name}, "cases/ValidationCases/AdditionalData/DevicesProfiles/HotWaterTank.json")

subclasses_dictionary["Device"]["WindTurbine"]("WT", BAU_contract_elec, wind_turbine_owner, aggregator_elec, {"device": "dummy_usage"}, {"wind_speed_daemon": wind_daemon.name}, "cases/ValidationCases/AdditionalData/DevicesProfiles/WT.json")


# ##############################################################################################
test_contract_datalogger = Datalogger("requests", "Requests", period="global")
test_contract_datalogger.add("physical_time", graph_status="X")
test_contract_datalogger.add("background_owner.LVE.energy_bought")


def dipslay_info():
    key_dict = test_contract_datalogger.request_keys(["physical_time","background_owner.LVE.energy_bought"])
    for key, value in key_dict.items():
        print(f"{key}: {value}")


# ##############################################################################################
# Simulation start
world.start(exogen_instruction=dipslay_info)






