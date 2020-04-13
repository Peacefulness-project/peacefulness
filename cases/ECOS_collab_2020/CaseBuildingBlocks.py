
from datetime import datetime

from src.common.World import World
from lib.DefaultNatures.DefaultNatures import load_low_voltage_electricity, load_low_temperature_heat
from src.common.Aggregator import Aggregator
from src.common.Agent import Agent
from src.common.Datalogger import Datalogger

from src.tools.SubclassesDictionary import get_subclasses
subclasses_dictionary = get_subclasses()


def create_world_with_set_parameters(strategy, DSM_proportion, sizing):

    # ##############################################################################################
    # Creation of the world
    # a world <=> a case, it contains all the model
    # a world needs just a name
    name_world = "ECOS_collab_2020"
    world = World(name_world)  # creation

    # ##############################################################################################
    # Definition of the path to the files
    pathExport = "cases/ECOS_collab_2020/Results/" + strategy + "_" + DSM_proportion + "_" + sizing  # directory where results are written
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
                   24 * 365*0+1)  # number of time steps simulated

    return world


def create_strategies(strategy):
    if strategy == "BAU":
        # the local electrical grid strategy
        supervisor_elec = subclasses_dictionary["Strategy"][f"AlwaysSatisfied"]()
    elif strategy == "Profitable":
        # the local electrical grid strategy
        supervisor_elec = subclasses_dictionary["Strategy"][f"WhenProfitableEmergency"]()
    else:
        # the local electrical grid strategy
        supervisor_elec = subclasses_dictionary["Strategy"][f"{strategy}Emergency"]()

    # the DHN strategy
    supervisor_heat = subclasses_dictionary["Strategy"][f"SubaggregatorHeatEmergency"]()

    # the national grid strategy
    grid_supervisor = subclasses_dictionary["Strategy"]["Grid"]()

    return {"elec": supervisor_elec, "heat": supervisor_heat, "grid": grid_supervisor}


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
    aggregator_elec = Aggregator(aggregator_name,  natures["elec"], strategies["elec"], aggregator_grid)  # creation of a aggregator

    # here we create another aggregator dedicated to heat
    aggregator_name = "Local_DHN"
    aggregator_heat = Aggregator(aggregator_name,  natures["heat"], strategies["heat"], aggregator_elec, 3.6, 3344)  # creation of a aggregator
    return {"grid": aggregator_grid, "elec": aggregator_elec, "heat": aggregator_heat}


def create_contracts(natures):
    flat_prices_elec = "flat_prices_elec"
    contract_elec = subclasses_dictionary["Contract"]["FlatEgoistContract"]("BAU_elec", natures["elec"], flat_prices_elec)

    flat_prices_heat = "flat_prices_heat"
    contract_heat = subclasses_dictionary["Contract"]["FlatEgoistContract"]("BAU_heat", natures["heat"], flat_prices_heat)

    return [{"elec": contract_elec, "heat": contract_heat}, {"elec": flat_prices_elec, "heat": flat_prices_heat}]


def create_agents():
    PV_producer = Agent("PV_producer")  # the owner of the PV panels

    solar_thermal_producer = Agent("solar_thermal_producer")  # the owner of the solar thermal collectors

    return {"elec": PV_producer, "heat": solar_thermal_producer}


def create_devices(world, aggregators, contracts, agents, price_IDs, DSM_proportion, sizing):
    if sizing == "mean":
        sizing_coeff_elec = 1
        sizing_coeff_heat = 1
    elif sizing == "peak":
        sizing_coeff_elec = 54000/18000
        sizing_coeff_heat = 23550/9350

    subclasses_dictionary["Device"]["PV"]("PV_field", contracts['elec'], agents['elec'], aggregators['elec'], "ECOS", "ECOS_field", {"surface": 18000 * sizing_coeff_elec})  # creation of a photovoltaic panel field

    subclasses_dictionary["Device"]["SolarThermalCollector"]("solar_thermal_collector_field", contracts['heat'], agents['heat'], aggregators['heat'], "ECOS", "ECOS_field", {"surface": 9350 * sizing_coeff_heat})  # creation of a solar thermal collector

    # repartition of contracts according to the chosen proportion
    if DSM_proportion == "high_DSM":
        BAU = 165
        DLC = 200
        curtailment = 135
    elif DSM_proportion == "low_DSM":
        BAU = 335
        DLC = 100
        curtailment = 65
    elif DSM_proportion == "no_DSM":
        BAU = 500
        DLC = 0
        curtailment = 0

    # BAU contracts
    world.agent_generation(BAU, "cases/ECOS_collab_2020/AgentTemplates/AgentECOS_1_BAU.json", [aggregators["elec"], aggregators["heat"]], {"LVE": price_IDs["elec"], "LTH": price_IDs["heat"]})
    world.agent_generation(BAU * 2, "cases/ECOS_collab_2020/AgentTemplates/AgentECOS_2_BAU.json", [aggregators["elec"], aggregators["heat"]], {"LVE": price_IDs["elec"], "LTH": price_IDs["heat"]})
    world.agent_generation(BAU, "cases/ECOS_collab_2020/AgentTemplates/AgentECOS_5_BAU.json", [aggregators["elec"], aggregators["heat"]], {"LVE": price_IDs["elec"], "LTH": price_IDs["heat"]})

    # DLC contracts
    world.agent_generation(DLC, "cases/ECOS_collab_2020/AgentTemplates/AgentECOS_1_DLC.json", [aggregators["elec"], aggregators["heat"]], {"LVE": price_IDs["elec"], "LTH": price_IDs["heat"]})
    world.agent_generation(DLC * 2, "cases/ECOS_collab_2020/AgentTemplates/AgentECOS_2_DLC.json", [aggregators["elec"], aggregators["heat"]], {"LVE": price_IDs["elec"], "LTH": price_IDs["heat"]})
    world.agent_generation(DLC, "cases/ECOS_collab_2020/AgentTemplates/AgentECOS_5_DLC.json", [aggregators["elec"], aggregators["heat"]], {"LVE": price_IDs["elec"], "LTH": price_IDs["heat"]})

    # Curtailment contracts
    world.agent_generation(curtailment, "cases/ECOS_collab_2020/AgentTemplates/AgentECOS_1_curtailment.json", [aggregators["elec"], aggregators["heat"]], {"LVE": price_IDs["elec"], "LTH": price_IDs["heat"]})
    world.agent_generation(curtailment * 2, "cases/ECOS_collab_2020/AgentTemplates/AgentECOS_2_curtailment.json", [aggregators["elec"], aggregators["heat"]], {"LVE": price_IDs["elec"], "LTH": price_IDs["heat"]})
    world.agent_generation(curtailment, "cases/ECOS_collab_2020/AgentTemplates/AgentECOS_5_curtailment.json", [aggregators["elec"], aggregators["heat"]], {"LVE": price_IDs["elec"], "LTH": price_IDs["heat"]})


def create_daemons(natures, price_IDs, sizing):
    # Price Managers
    # these daemons fix a price for a given nature of energy
    if sizing == "peak":
        subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("LVE_tariffs", 1, {"nature": natures["elec"].name, "buying_price": [0.4375, 0.3125], "selling_price": [0.245, 0.245], "hours": [[6, 12], [14, 23]], "identifier": price_IDs["elec"]})  # sets prices for TOU rate
        subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("Heat_tariffs", 1, {"nature": natures["heat"].name, "buying_price": 0.5125, "selling_price": 0.407, "identifier": price_IDs["heat"]})  # sets prices for the system operator

        subclasses_dictionary["Daemon"]["GridPricesDaemon"]("grid_prices_heat", 1, {"nature": natures["heat"].name, "grid_buying_price": 0.407, "grid_selling_price": 0})  # sets prices for the system operator
    elif sizing == "mean":
        subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("LVE_tariffs", 1, {"nature": natures["elec"].name, "buying_price": [0.2125, 0.15], "selling_price": [0.112, 0.112], "hours": [[6, 12], [14, 23]], "identifier": price_IDs["elec"]})  # sets prices for TOU rate
        subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("Heat_tariffs", 1, {"nature": natures["heat"].name, "buying_price": 0.30, "selling_price": 0.234, "identifier": price_IDs["heat"]})  # sets prices for the system operator

        subclasses_dictionary["Daemon"]["GridPricesDaemon"]("grid_prices_heat", 1, {"nature": natures["heat"].name, "grid_buying_price": 0.234, "grid_selling_price": 0})  # sets prices for the system operator

    subclasses_dictionary["Daemon"]["GridPricesDaemon"]("grid_prices_elec", 1, {"nature": natures["elec"].name, "grid_buying_price": 0.2, "grid_selling_price": 0.1})  # sets prices for the system operator

    # Outdoor temperature
    # this daemon is responsible for the value of outdoor temperature in the catalog
    subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Pau"})

    # Indoor temperature
    # this daemon is responsible for the value of indoor temperatures in the catalog
    subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]("Asie")

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
    producer_datalogger.add(f"solar_thermal_producer.LTH.energy_erased")
    producer_datalogger.add(f"PV_producer.LVE.energy_sold")
    producer_datalogger.add(f"solar_thermal_producer.LTH.energy_sold")

    producer_datalogger.add(f"PV_field_exergy_in")
    producer_datalogger.add(f"solar_thermal_collector_field_exergy_in")
    producer_datalogger.add(f"PV_field_exergy_out")
    producer_datalogger.add(f"solar_thermal_collector_field_exergy_out")


