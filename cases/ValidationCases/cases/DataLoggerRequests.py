# This script checks that the dataloggher request_function works well.

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
BAU_strategy = subclasses_dictionary["Strategy"]["AlwaysSatisfied"]()

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


# ##############################################################################################
test_datalogger_1 = Datalogger("requests_1", "Requests", period=1)
test_datalogger_1.add("simulation_time")
test_datalogger_1.add("physical_time", graph_status="X")
test_datalogger_1.add("background_owner.LVE.energy_bought")
expected_values_1 = {"physical_time": ["2000-01-01 00:00:00", "2000-01-01 01:00:00", "2000-01-01 02:00:00", "2000-01-01 03:00:00", "2000-01-01 04:00:00", "2000-01-01 05:00:00", "2000-01-01 06:00:00", "2000-01-01 07:00:00", "2000-01-01 08:00:00", "2000-01-01 09:00:00", "2000-01-01 10:00:00", "2000-01-01 11:00:00", "2000-01-01 12:00:00", "2000-01-01 13:00:00", "2000-01-01 14:00:00", "2000-01-01 15:00:00", "2000-01-01 16:00:00", "2000-01-01 17:00:00", "2000-01-01 18:00:00", "2000-01-01 19:00:00", "2000-01-01 20:00:00", "2000-01-01 21:00:00", "2000-01-01 22:00:00", "2000-01-01 23:00:00"],
                     "background_owner.LVE.energy_bought": [0, 1., 2., 3., 4., 5., 6., 7., 8., 9., 10., 11., 12., 13., 14., 15., 16., 17., 18., 19., 20., 21., 22., 23.]}

test_datalogger_3 = Datalogger("requests_3", "Requests", period=3)
test_datalogger_3.add("simulation_time")
test_datalogger_3.add("physical_time", graph_status="X")
test_datalogger_3.add("background_owner.LVE.energy_bought")
expected_values_3 = {"physical_time": ["2000-01-01 00:00:00", "2000-01-01 03:00:00", "2000-01-01 06:00:00", "2000-01-01 09:00:00", "2000-01-01 12:00:00", "2000-01-01 15:00:00", "2000-01-01 18:00:00", "2000-01-01 21:00:00", "2000-01-01 21:00:00"],
                     "background_owner.LVE.energy_bought.mean": [0., 2., 5., 8., 11., 14., 17., 20., 23.],
                     "background_owner.LVE.energy_bought.min": [0, 1., 4., 7., 10., 13., 16., 19., 22., 23.],
                     "background_owner.LVE.energy_bought.max": [0, 3., 6., 9., 12., 15., 18., 21., 23.],
                     "background_owner.LVE.energy_bought.sum": [0, 6., 15., 24., 33., 42., 51., 60., 69.]
                     }


i = [0]
def check_values():
    # frequency 1
    key_dict = test_datalogger_1.request_keys(["simulation_time", "physical_time", "background_owner.LVE.energy_bought"])
    simulation_time = key_dict["simulation_time"]
    for key in expected_values_1:
        if str(expected_values_1[key][simulation_time]) != str(key_dict[key]):
            print((expected_values_1[key][simulation_time]), (key_dict[key]))
            raise Exception(f"A problem has been encountered at {simulation_time}")

    # frequency 3
    if simulation_time % 3 == 0 or simulation_time == 23:
        key_dict = test_datalogger_3.request_keys(["simulation_time", "physical_time", "background_owner.LVE.energy_bought"])
        if str(expected_values_3["physical_time"][simulation_time//3]) != str(key_dict["physical_time"]):
            print((expected_values_3["physical_time"][simulation_time//3]), (key_dict["physical_time"]))

        if str(expected_values_3["background_owner.LVE.energy_bought.mean"][i[0]]) != str(key_dict["background_owner.LVE.energy_bought"]["mean"]):
            print((expected_values_3["background_owner.LVE.energy_bought.mean"][i[0]]), (key_dict["background_owner.LVE.energy_bought"]["mean"]))
        if str(expected_values_3["background_owner.LVE.energy_bought.min"][i[0]]) != str(key_dict["background_owner.LVE.energy_bought"]["min"]):
            print((expected_values_3["background_owner.LVE.energy_bought.min"][i[0]]), (key_dict["background_owner.LVE.energy_bought"]["min"]))
        if str(expected_values_3["background_owner.LVE.energy_bought.max"][i[0]]) != str(key_dict["background_owner.LVE.energy_bought"]["max"]):
            print((expected_values_3["background_owner.LVE.energy_bought.max"][i[0]]), (key_dict["background_owner.LVE.energy_bought"]["max"]))
        if str(expected_values_3["background_owner.LVE.energy_bought.sum"][i[0]]) != str(key_dict["background_owner.LVE.energy_bought"]["sum"]):
            print((expected_values_3["background_owner.LVE.energy_bought.sum"][i[0]]), (key_dict["background_owner.LVE.energy_bought"]["sum"]))
        i[0] += 1

# for key in key_list:
    #     if str(expected_values_3[key][simulation_time]) != str(key_dict[key]):
    #         print((expected_values_3[key][simulation_time]), (key_dict[key]))
            # raise Exception(f"A problem has been encountered at {simulation_time}")


# ##############################################################################################
# Simulation start
world.start(exogen_instruction=check_values)






