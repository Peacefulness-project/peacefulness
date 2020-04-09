from datetime import datetime

from src.common.World import World
from lib.DefaultNatures.DefaultNatures import load_low_voltage_electricity, load_low_temperature_heat, load_high_temperature_coldness
from src.common.Aggregator import Aggregator

from src.tools.SubclassesDictionary import get_subclasses
subclasses_dictionary = get_subclasses()


def create_world_with_set_parameters(city_case, city_weather):

    # ##############################################################################################
    # Creation of the world
    # a world <=> a case, it contains all the model
    # a world needs just a name
    name_world = city_case + "_city"
    world = World(name_world)  # creation

    # ##############################################################################################
    # Definition of the path to the files
    pathExport = "cases/Edwin_profiles/Results/" + city_case + "_weather_" + city_weather  # directory where results are written
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


def create_contracts(natures):
    flat_prices_elec = "flat_prices_elec"
    subclasses_dictionary["Contract"]["FlatEgoistContract"]("BAU_elec", natures["elec"], flat_prices_elec)

    flat_prices_heat = "flat_prices_heat"
    subclasses_dictionary["Contract"]["FlatEgoistContract"]("BAU_heat", natures["heat"], flat_prices_heat)

    flat_prices_cold = "flat_prices_cold"
    subclasses_dictionary["Contract"]["FlatEgoistContract"]("BAU_cold", natures["cold"], flat_prices_cold)

    return {"elec": flat_prices_elec, "heat": flat_prices_heat, "cold": flat_prices_cold}


def create_devices(world, aggregators, price_IDs, country, weather_city):
    # BAU contracts
    world.agent_generation(15, "cases/Edwin_profiles/AgentTemplates/Apartment_1_" + country + "_" + weather_city + ".json", [aggregators["elec"], aggregators["heat"], aggregators["cold"]], {"LVE": price_IDs["elec"], "LTH": price_IDs["heat"], "HTC": price_IDs["cold"]})
    world.agent_generation(20, "cases/Edwin_profiles/AgentTemplates/Apartment_2_" + country + "_" + weather_city + ".json", [aggregators["elec"], aggregators["heat"], aggregators["cold"]], {"LVE": price_IDs["elec"], "LTH": price_IDs["heat"], "HTC": price_IDs["cold"]})
    world.agent_generation(15, "cases/Edwin_profiles/AgentTemplates/Apartment_5_" + country + "_" + weather_city + ".json", [aggregators["elec"], aggregators["heat"], aggregators["cold"]], {"LVE": price_IDs["elec"], "LTH": price_IDs["heat"], "HTC": price_IDs["cold"]})


def create_daemons(natures, price_IDs, weather):
    # Price Managers
    # this daemons fix a price for a given nature of energy
    subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("LVE_tariffs", 1, {"nature": natures["elec"].name, "buying_price": 0, "selling_price": 0, "identifier": price_IDs["elec"]})  # sets prices for TOU rate
    subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("Heat_tariffs", 1, {"nature": natures["heat"].name, "buying_price": 0, "selling_price": 0, "identifier": price_IDs["heat"]})  # sets prices for the system operator
    subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("Cold_tariffs", 1, {"nature": natures["cold"].name, "buying_price": 0, "selling_price": 0, "identifier": price_IDs["cold"]})  # sets prices for the system operator

    subclasses_dictionary["Daemon"]["GridPricesDaemon"]("grid_prices_elec", 1, {"nature": natures["elec"].name, "grid_buying_price": 0, "grid_selling_price": 0})  # sets prices for the system operator
    subclasses_dictionary["Daemon"]["GridPricesDaemon"]("grid_prices_heat", 1, {"nature": natures["heat"].name, "grid_buying_price": 0, "grid_selling_price": 0})  # sets prices for the system operator
    subclasses_dictionary["Daemon"]["GridPricesDaemon"]("grid_prices_cold", 1, {"nature": natures["cold"].name, "grid_buying_price": 0, "grid_selling_price": 0})  # sets prices for the system operator

    # Outdoor temperature
    # this daemon is responsible for the value of outdoor temperature in the catalog
    subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]("Azzie", {"location": weather})

    # Indoor temperature
    # this daemon is responsible for the value of indoor temperatures in the catalog
    subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]("Asie")

    # Water temperature
    # this daemon is responsible for the value of the water temperature in the catalog
    subclasses_dictionary["Daemon"]["ColdWaterDaemon"]("Mephisto", {"location": "Pau"})


def create_dataloggers():
    subclasses_dictionary["Datalogger"]["NatureBalanceDatalogger"]()

