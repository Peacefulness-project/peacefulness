# This script is here to help not loose yourself when creating a case.

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

from time import process_time


def simulation(season):

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
    name_world = "your_name"
    world = World(name_world)  # creation

    # ##############################################################################################
    # Definition of the path to the files
    world.set_directory("cases/Studies/PresentationArticleCases/Results/LittleScaleCase/"+season+"/")  # here, you have to put the path to your results directory

    # ##############################################################################################
    # Definition of the random seed
    # The default seed is the current time (the value returned by datetime.now())
    world.set_random_seed("sunflower")

    # ##############################################################################################
    # Time parameters
    # it needs a start date, the value of an iteration in hours and the total number of iterations
    if season == "winter":
        start_date = datetime(year=1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)  # a start date in the datetime format
    elif season == "spring":
        start_date = datetime(year=1, month=4, day=1, hour=0, minute=0, second=0, microsecond=0)  # a start date in the datetime format
    elif season == "summer":
        start_date = datetime(year=1, month=7, day=1, hour=0, minute=0, second=0, microsecond=0)  # a start date in the datetime format
    elif season == "autumn":
        start_date = datetime(year=1, month=10, day=1, hour=0, minute=0, second=0, microsecond=0)  # a start date in the datetime format

    world.set_time(start_date,  # time management: start date
                   1,  # value of a time step (in hours)
                   24 * 7)  # number of time steps simulated

    # ##############################################################################################
    # Model
    # ##############################################################################################

    # ##############################################################################################
    # Creation of nature
    LVE = load_low_voltage_electricity()

    # ##############################################################################################
    # Creation of daemons

    # Price Managers
    price_manager_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_elec", {"nature": LVE.name, "buying_price": 0.15/0.9, "selling_price": 0.10})  # sets prices for flat rate

    # Limit Prices
    limit_price_elec = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0.2, "limit_selling_price": 0.1})  # sets prices for the system operator

    # Indoor temperature
    indoor_temperature_daemon = subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

    # Outdoor temperature
    outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Pau"})

    # Water temperature
    cold_water_temperature_daemon = subclasses_dictionary["Daemon"]["ColdWaterTemperatureDaemon"]({"location": "France"})

    # Irradiation
    irradiation_daemon = subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Pau"})

    # ##############################################################################################
    # Creation of strategies
    strategy_grid = subclasses_dictionary["Strategy"]["Grid"]()

    strategy_elec = subclasses_dictionary["Strategy"]["LightAutarkyEmergency"]()

    # ##############################################################################################
    # Manual creation of agents
    house_owner = Agent("house_owner")

    aggregator_owner = Agent("aggregator_owner")

    # ##############################################################################################
    # Manual creation of contracts
    cooperative_elec_contract = subclasses_dictionary["Contract"]["CooperativeContract"]("cooperative_contract_elec", LVE, price_manager_elec)

    egoist_elec_contract = subclasses_dictionary["Contract"]["EgoistContract"]("egoist_contract_elec", LVE, price_manager_elec)

    # ##############################################################################################
    # Creation of aggregators
    national_grid = Aggregator("national_grid", LVE, strategy_grid, aggregator_owner)

    local_grid = Aggregator("local_grid", LVE, strategy_elec, aggregator_owner, national_grid, egoist_elec_contract)

    # ##############################################################################################
    # Manual creation of devices
    subclasses_dictionary["Device"]["Heating"]("heating", cooperative_elec_contract, house_owner, local_grid, {"user": "residential", "device": "house_elec"}, {"outdoor_temperature_daemon": outdoor_temperature_daemon})

    subclasses_dictionary["Device"]["Background"]("background", cooperative_elec_contract, house_owner, local_grid, {"user": "family", "device": "single"})

    subclasses_dictionary["Device"]["HotWaterTank"]("hot_water_tank", cooperative_elec_contract, house_owner, local_grid, {"user": "ECOS_5", "device": "5_people_elec"}, {"cold_water_temperature_daemon": cold_water_temperature_daemon})

    subclasses_dictionary["Device"]["Dishwasher"]("dishwasher", cooperative_elec_contract, house_owner, local_grid, {"user": "family", "device": "medium_consumption"})

    subclasses_dictionary["Device"]["WashingMachine"]("washing_machine", cooperative_elec_contract, house_owner, local_grid, {"user": "family", "device": "medium_consumption"})

    subclasses_dictionary["Device"]["Dryer"]("dryer", cooperative_elec_contract, house_owner, local_grid, {"user": "family", "device": "medium_consumption"})

    subclasses_dictionary["Device"]["PV"]("PV", egoist_elec_contract, house_owner, local_grid, {"device": "standard_field"}, {"panels": 5, "irradiation_daemon": irradiation_daemon})

    # ##############################################################################################
    # Creation of dataloggers

    # ##############################################################################################
    # Simulation start

    # Performance measurement
    CPU_time = process_time()

    world.start()

    # CPU time measurement
    CPU_time = process_time() - CPU_time  # time taken by the initialization
    filename = world._catalog.get("path") + "outputs/CPU_time.txt"  # adapting the path to the OS
    file = open(filename, "a")  # creation of the file
    file.write(f"time taken by the calculation phase: {CPU_time}\n")
    file.close()


