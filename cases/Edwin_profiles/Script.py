from datetime import datetime

from src.common.World import World
from lib.DefaultNatures.DefaultNatures import load_low_voltage_electricity, load_low_temperature_heat, load_high_temperature_coldness
from src.common.Aggregator import Aggregator
from src.common.Agent import Agent

from src.tools.SubclassesDictionary import get_subclasses
subclasses_dictionary = get_subclasses()


def simulation(habits, weather_city, set_point):
    # ##############################################################################################
    # Initialization
    # ##############################################################################################

    # ##############################################################################################
    # Creation of the world
    # a world <=> a case, it contains all the model
    # a world needs just a name
    name_world = weather_city + "_city"
    world = World(name_world)  # creation

    # ##############################################################################################
    # Definition of the path to the files
    pathExport = "cases/Edwin_profiles/Results/" + habits + "_habits_" + weather_city + "_weather_" + set_point + "_set_point"  # directory where results are written
    world.set_directory(pathExport)  # registration

    # ##############################################################################################
    # Definition of the random seed to be used
    # The default seed is the current time (the value returned by datetime.now())
    world.set_random_seed("tournesol")

    # ##############################################################################################
    # Time Manager
    # it needs a start date, the value of an iteration in hours and the total number of iterations
    start_date = datetime.now()  # a start date in the datetime format
    start_date = start_date.replace(year=2019, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    world.set_time(start_date,  # time management: start date
                   1,  # value of a time step (in hours)
                   24 * 365)  # number of time steps simulated

    # ##############################################################################################
    # Model creation
    # ##############################################################################################

    # ##############################################################################################
    # Strategies
    # BAU strategy
    supervisor_BAU = subclasses_dictionary["Strategy"]["AlwaysSatisfied"]()

    # the supervisor grid, which always proposes an infinite quantity to sell and to buy
    grid_supervisor = subclasses_dictionary["Strategy"]["Grid"]()

    # ##############################################################################################
    # Natures
    # low voltage electricity
    LVE = load_low_voltage_electricity()

    # low temperature heat
    LTH = load_low_temperature_heat()

    # high temperature coldness
    HTC = load_high_temperature_coldness()

    # ##############################################################################################
    # Daemons
    # Price Managers
    # this daemons fix a price for a given nature of energy
    price_managing_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices_elec", {"nature": LVE.name, "buying_price": 0, "selling_price": 0})  # sets prices for TOU rate
    price_managing_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices_heat", {"nature": LTH.name, "buying_price": 0, "selling_price": 0})  # sets prices for the system operator
    price_managing_cold = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices_cold", {"nature": HTC.name, "buying_price": 0, "selling_price": 0})  # sets prices for the system operator

    subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0, "limit_selling_price": 0})  # sets prices for the system operator
    subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 0, "limit_selling_price": 0})  # sets prices for the system operator
    subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": HTC.name, "limit_buying_price": 0, "limit_selling_price": 0})  # sets prices for the system operator

    # Outdoor temperature
    # this daemon is responsible for the value of outdoor temperature in the catalog
    subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": weather_city})

    # Indoor temperature
    # this daemon is responsible for the value of indoor temperatures in the catalog
    subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

    # Water temperature
    # this daemon is responsible for the value of the water temperature in the catalog
    subclasses_dictionary["Daemon"]["ColdWaterDaemon"]({"location": "Pau"})

    # ##############################################################################################
    # Agents
    local_electrical_grid = Agent("local_electrical_grid_manager")

    local_DHN = Agent("local_DHN_manager")

    local_DCN = Agent("local_DCN_manager")

    national_grid = Agent("national_grid")

    # ##############################################################################################
    # Contracts
    contract_elec = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_elec", LVE, price_managing_elec)

    contract_heat = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_heat", LTH, price_managing_heat)

    contract_cold = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_cold", HTC, price_managing_cold)

    # ##############################################################################################
    # Aggregators
    # and then we create a third who represents the grid
    aggregator_name = "Enedis"
    aggregator_grid = Aggregator(aggregator_name, LVE, grid_supervisor, national_grid)

    # here we create a second one put under the orders of the first
    aggregator_name = "general_aggregator"
    aggregator_elec = Aggregator(aggregator_name,  LVE, supervisor_BAU, local_electrical_grid, aggregator_grid, contract_elec)  # creation of a aggregator

    # here we create another aggregator dedicated to heat
    aggregator_name = "Local_DHN"
    aggregator_heat = Aggregator(aggregator_name, LTH, supervisor_BAU, local_DHN, aggregator_grid, contract_heat)  # creation of a aggregator

    # here we create another aggregator dedicated to cold
    aggregator_name = "Local_DCN"
    aggregator_cold = Aggregator(aggregator_name,  HTC, supervisor_BAU, local_DCN, aggregator_grid, contract_cold)  # creation of a aggregator

    # ##############################################################################################
    # Devices
    # BAU contracts
    world.agent_generation(15, "cases/Edwin_profiles/AgentTemplates/Apartment_1_" + weather_city + "_weather_" + habits + "_habits_" + set_point + "_set_point.json", [aggregator_elec, aggregator_heat, aggregator_cold], {"LVE": price_managing_elec, "LTH": price_managing_heat, "HTC": price_managing_cold})
    world.agent_generation(20, "cases/Edwin_profiles/AgentTemplates/Apartment_2_" + weather_city + "_weather_" + habits + "_habits_" + set_point + "_set_point.json", [aggregator_elec, aggregator_heat, aggregator_cold], {"LVE": price_managing_elec, "LTH": price_managing_heat, "HTC": price_managing_cold})
    world.agent_generation(15, "cases/Edwin_profiles/AgentTemplates/Apartment_5_" + weather_city + "_weather_" + habits + "_habits_" + set_point + "_set_point.json", [aggregator_elec, aggregator_heat, aggregator_cold], {"LVE": price_managing_elec, "LTH": price_managing_heat, "HTC": price_managing_cold})

    # ##############################################################################################
    # Dataloggers
    subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"]()

    # ##############################################################################################
    # Simulation
    # ##############################################################################################
    world.start()
