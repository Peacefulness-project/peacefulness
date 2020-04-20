from datetime import datetime

from src.common.World import World
from lib.DefaultNatures.DefaultNatures import *
from src.common.Aggregator import Aggregator
from src.common.Agent import Agent
from src.common.Datalogger import Datalogger

from src.tools.SubclassesDictionary import get_subclasses
subclasses_dictionary = get_subclasses()


def create_world_with_set_parameters(chosen_strategy, renewable_capacity):

    # ##############################################################################################
    # Creation of the world
    # a world <=> a case, it contains all the model
    # a world needs just a name
    name_world = chosen_strategy + "_" + renewable_capacity + "_renewable"
    world = World(name_world)  # creation

    # ##############################################################################################
    # Definition of the path to the files
    pathExport = "cases/Edwin_profiles/Results/" + chosen_strategy + "_" + renewable_capacity + "_renewable"  # directory where results are written
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


def create_strategies(chosen_strategy):
    if chosen_strategy == "strategy_1":
        supervisor = subclasses_dictionary["Strategy"]["AlwaysSatisfied"]()
    elif chosen_strategy == "strategy_2":
        supervisor = subclasses_dictionary["Strategy"][f"LightAutarkyEmergency"]()

    # the DHN strategy
    supervisor_heat = subclasses_dictionary["Strategy"][f"SubaggregatorHeatEmergency"]()

    # the supervisor grid, which always proposes an infinite quantity to sell and to buy
    grid_supervisor = subclasses_dictionary["Strategy"]["Grid"]()

    return {"BAU": supervisor, "grid": grid_supervisor, "heat": supervisor_heat}


def create_natures():
    # low voltage electricity
    LVE = load_low_voltage_electricity()

    # low temperature heat
    LTH = load_low_temperature_heat()

    return {"elec": LVE, "heat": LTH}


def create_aggregators(natures, strategies):
    # and then we create a third who represents the grid
    aggregator_name = "Enedis"
    aggregator_grid = Aggregator(aggregator_name, natures["elec"], strategies["grid"])

    # here we create a second one put under the orders of the first
    aggregator_name = "general_aggregator"
    aggregator_elec = Aggregator(aggregator_name,  natures["elec"], strategies["BAU"], aggregator_grid)  # creation of a aggregator

    # here we create another aggregator dedicated to heat
    aggregator_name = "Local_DHN"
    aggregator_heat = Aggregator(aggregator_name,  natures["heat"], strategies["heat"], aggregator_elec, 3.6, 2000)  # creation of a aggregator

    return {"grid": aggregator_grid, "elec": aggregator_elec, "heat": aggregator_heat}


def create_contracts(natures):
    flat_prices_elec = "flat_prices_elec"
    contratc_elec = subclasses_dictionary["Contract"]["FlatEgoistContract"]("BAU_elec", natures["elec"], flat_prices_elec)

    flat_prices_heat = "flat_prices_heat"
    contract_heat = subclasses_dictionary["Contract"]["FlatEgoistContract"]("BAU_heat", natures["heat"], flat_prices_heat)

    return [{"elec": contratc_elec, "heat": contract_heat}, {"elec": flat_prices_elec, "heat": flat_prices_heat}]


def create_agents():
    PV_producer = Agent("PV_producer")  # the owner of the PV panels

    DHN_producer = Agent("DHN_producer")  # the owner of the

    return {"PV": PV_producer, "DHN": DHN_producer}


def create_devices(world, aggregators, contracts, agents, price_IDs, renewable_capacity):
    if renewable_capacity == "little":
        subclasses_dictionary["Device"]["PV"]("PV_field", contracts['elec'], agents['PV'], aggregators['elec'], "ECOS", "ECOS_field", {"surface": 1000})  # creation of a photovoltaic panel field
    elif renewable_capacity == "a_lot":
        subclasses_dictionary["Device"]["PV"]("PV_field", contracts['elec'], agents['PV'], aggregators['elec'], "ECOS", "ECOS_field", {"surface": 3000})  # creation of a photovoltaic panel field

    subclasses_dictionary["Device"]["GenericProducer"]("heat_production", contracts['heat'], agents['DHN'], aggregators['heat'], "ECOS", "ECOS")  # creation of a heat production unit

    # DLC contracts
    world.agent_generation(1000, "cases/DummySeriesOfCases/AgentTemplates/dummy_agent_template.json", [aggregators["elec"], aggregators["heat"]], {"LVE": price_IDs["elec"], "LTH": price_IDs["heat"]})


def create_daemons(natures, price_IDs):
    # Price Managers
    # these daemons fix a price for a given nature of energy
    subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"](1, {"nature": natures["elec"].name, "buying_price": [0.12, 0.17], "selling_price": [0.11, 0.11], "hours": [[6, 12], [14, 23]], "identifier": price_IDs["elec"]})  # sets prices for TOU rate
    subclasses_dictionary["Daemon"]["PriceManagerDaemon"](1, {"nature": natures["heat"].name, "buying_price": 0.1, "selling_price": 0.08, "identifier": price_IDs["heat"]})  # sets prices for the system operator

    subclasses_dictionary["Daemon"]["GridPricesDaemon"](1, {"nature": natures["elec"].name, "grid_buying_price": 0.18, "grid_selling_price": 0.05})  # sets prices for the system operator
    subclasses_dictionary["Daemon"]["GridPricesDaemon"](1, {"nature": natures["heat"].name, "grid_buying_price": 0.10, "grid_selling_price": 0.08})  # sets prices for the system operator

    # Outdoor temperature
    # this daemon is responsible for the value of outdoor temperature in the catalog
    subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Pau"})

    # Indoor temperature
    # this daemon is responsible for the value of indoor temperatures in the catalog
    subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

    # Water temperature
    # this daemon is responsible for the value of the water temperature in the catalog
    subclasses_dictionary["Daemon"]["ColdWaterDaemon"]({"location": "Pau"})

    # Irradiation
    # this daemon is responsible for updating the value of raw solar irradiation
    subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Pau"})


def create_dataloggers():
    # datalogger for balances
    # these dataloggers record the balances for each agent, contract, nature and  cluster
    subclasses_dictionary["Datalogger"]["ContractBalanceDatalogger"]()
    subclasses_dictionary["Datalogger"]["AggregatorBalanceDatalogger"]()
    subclasses_dictionary["Datalogger"]["NatureBalanceDatalogger"]()

    subclasses_dictionary["Datalogger"]["ECOSAggregatorDatalogger"]()
    subclasses_dictionary["Datalogger"]["GlobalValuesDatalogger"]()

    # datalogger used to get back producer outputs
    producer_datalogger = Datalogger("producer_datalogger", "ProducerBalances.txt")

    producer_datalogger.add(f"PV_producer.LVE.energy_erased")
    producer_datalogger.add(f"DHN_producer.LTH.energy_erased")
    producer_datalogger.add(f"PV_producer.LVE.energy_sold")
    producer_datalogger.add(f"DHN_producer.LTH.energy_sold")

