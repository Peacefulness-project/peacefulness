from datetime import datetime

from src.common.World import World
from lib.DefaultNatures.DefaultNatures import load_low_voltage_electricity, load_low_temperature_heat, load_high_temperature_coldness
from src.common.Aggregator import Aggregator

from src.tools.SubclassesDictionary import get_subclasses
subclasses_dictionary = get_subclasses()


def create_world_with_set_parameters(habits, city_weather, set_point):

    # ##############################################################################################
    # Creation of the world
    # a world <=> a case, it contains all the model
    # a world needs just a name
    name_world = city_weather + "_city"
    world = World(name_world)  # creation

    # ##############################################################################################
    # Definition of the path to the files
    pathExport = "cases/Edwin_profiles/Results/" + habits + "_habits_" + city_weather + "_weather_" + set_point + "_set_point"  # directory where results are written
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

    return world


def create_strategies():
    # BAU strategy
    supervisor_BAU = subclasses_dictionary["Strategy"]["AlwaysSatisfied"]()

    # the supervisor grid, which always proposes an infinite quantity to sell and to buy
    grid_supervisor = subclasses_dictionary["Strategy"]["Grid"]()

    return {"BAU": supervisor_BAU, "grid": grid_supervisor}


def create_natures():
    # low voltage electricity
    LVE = load_low_voltage_electricity()

    # low temperature heat
    LTH = load_low_temperature_heat()

    # high temperature coldness
    HTC = load_high_temperature_coldness()

    return {"elec": LVE, "heat": LTH, "cold": HTC}


def create_daemons(natures, city_weather):
    # Price Managers
    # this daemons fix a price for a given nature of energy
    price_managing_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices_elec", {"nature": natures["elec"].name, "buying_price": 0, "selling_price": 0})  # sets prices for TOU rate
    price_managing_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices_heat", {"nature": natures["heat"].name, "buying_price": 0, "selling_price": 0})  # sets prices for the system operator
    price_managing_cold = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices_cold", {"nature": natures["cold"].name, "buying_price": 0, "selling_price": 0})  # sets prices for the system operator

    subclasses_dictionary["Daemon"]["GridPricesDaemon"]({"nature": natures["elec"].name, "grid_buying_price": 0, "grid_selling_price": 0})  # sets prices for the system operator
    subclasses_dictionary["Daemon"]["GridPricesDaemon"]({"nature": natures["heat"].name, "grid_buying_price": 0, "grid_selling_price": 0})  # sets prices for the system operator
    subclasses_dictionary["Daemon"]["GridPricesDaemon"]({"nature": natures["cold"].name, "grid_buying_price": 0, "grid_selling_price": 0})  # sets prices for the system operator

    # Outdoor temperature
    # this daemon is responsible for the value of outdoor temperature in the catalog
    subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": city_weather})

    # Indoor temperature
    # this daemon is responsible for the value of indoor temperatures in the catalog
    subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

    # Water temperature
    # this daemon is responsible for the value of the water temperature in the catalog
    subclasses_dictionary["Daemon"]["ColdWaterDaemon"]({"location": "Pau"})

    return {"elec": price_managing_elec, "heat": price_managing_heat, "cold": price_managing_cold}


def create_aggregators(natures, strategies):
    # and then we create a third who represents the grid
    aggregator_name = "Enedis"
    aggregator_grid = Aggregator(aggregator_name, natures["elec"], strategies["grid"])

    # here we create a second one put under the orders of the first
    aggregator_name = "general_aggregator"
    aggregator_elec = Aggregator(aggregator_name,  natures["elec"], strategies["BAU"], aggregator_grid)  # creation of a aggregator

    # here we create another aggregator dedicated to heat
    aggregator_name = "Local_DHN"
    aggregator_heat = Aggregator(aggregator_name,  natures["heat"], strategies["BAU"], aggregator_grid)  # creation of a aggregator

    # here we create another aggregator dedicated to cold
    aggregator_name = "Local_DCN"
    aggregator_cold = Aggregator(aggregator_name,  natures["cold"], strategies["BAU"], aggregator_grid)  # creation of a aggregator

    return {"grid": aggregator_grid, "elec": aggregator_elec, "heat": aggregator_heat, "cold": aggregator_cold}


def create_contracts(natures, price_managing):
    subclasses_dictionary["Contract"]["FlatEgoistContract"]("BAU_elec", natures["elec"], price_managing["elec"])

    subclasses_dictionary["Contract"]["FlatEgoistContract"]("BAU_heat", natures["heat"], price_managing["heat"])

    subclasses_dictionary["Contract"]["FlatEgoistContract"]("BAU_cold", natures["cold"], price_managing["cold"])


def create_devices(world, aggregators, price_managing_daemons, weather_city, habits, set_point):
    # BAU contracts
    world.agent_generation(15, "cases/Edwin_profiles/AgentTemplates/Apartment_1_" + weather_city + "_weather_" + habits + "_habits_" + set_point + "_set_point.json", [aggregators["elec"], aggregators["heat"], aggregators["cold"]], {"LVE": price_managing_daemons["elec"], "LTH": price_managing_daemons["heat"], "HTC": price_managing_daemons["cold"]})
    world.agent_generation(20, "cases/Edwin_profiles/AgentTemplates/Apartment_2_" + weather_city + "_weather_" + habits + "_habits_" + set_point + "_set_point.json", [aggregators["elec"], aggregators["heat"], aggregators["cold"]], {"LVE": price_managing_daemons["elec"], "LTH": price_managing_daemons["heat"], "HTC": price_managing_daemons["cold"]})
    world.agent_generation(15, "cases/Edwin_profiles/AgentTemplates/Apartment_5_" + weather_city + "_weather_" + habits + "_habits_" + set_point + "_set_point.json", [aggregators["elec"], aggregators["heat"], aggregators["cold"]], {"LVE": price_managing_daemons["elec"], "LTH": price_managing_daemons["heat"], "HTC": price_managing_daemons["cold"]})


def create_dataloggers():
    subclasses_dictionary["Datalogger"]["NatureBalanceDatalogger"]()

