from datetime import datetime

from src.common.World import World
from lib.DefaultNatures.DefaultNatures import load_low_voltage_electricity
from src.common.Aggregator import Aggregator
from src.common.Agent import Agent
from src.common.Datalogger import Datalogger

from src.tools.SubclassesDictionary import get_subclasses
subclasses_dictionary = get_subclasses()


def create_world_with_set_parameters(exchange_strategy, distribution_strategy, renewable_proportion, DSM_proportion):

    # ##############################################################################################
    # Creation of the world
    # a world <=> a case, it contains all the model
    # a world needs just a name
    name_world = "ECOS_test_cases_2020"
    world = World(name_world)  # creation

    # ##############################################################################################
    # Definition of the path to the files
    pathExport = "cases/ECOS_TestCases_2020/Results/" + exchange_strategy + "_" + distribution_strategy + "_" + DSM_proportion + "_" + renewable_proportion  # directory where results are written
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


def create_strategies(exchange_strategy, distribution_strategy):
    if exchange_strategy == "BAU":
        # the local electrical grid strategy
        supervisor_elec = subclasses_dictionary["Strategy"][f"AlwaysSatisfied"]()
    elif exchange_strategy == "Profitable":
        # the local electrical grid strategy
        supervisor_elec = subclasses_dictionary["Strategy"][f"WhenProfitable{distribution_strategy}"]()
    else:
        # the local electrical grid strategy
        supervisor_elec = subclasses_dictionary["Strategy"][f"Autarky{distribution_strategy}"]()

    # the national grid strategy
    grid_supervisor = subclasses_dictionary["Strategy"]["Grid"]()

    return {"elec": supervisor_elec, "grid": grid_supervisor}


def create_natures():
    # low voltage electricity
    LVE = load_low_voltage_electricity()

    return {"elec": LVE}


def create_aggregators(natures, strategies):
    # and then we create a third who represents the grid
    aggregator_name = "Enedis"
    aggregator_grid = Aggregator(aggregator_name, natures["elec"], strategies["grid"])

    # here we create a second one put under the orders of the first
    aggregator_name = "general_aggregator"
    aggregator_elec = Aggregator(aggregator_name,  natures["elec"], strategies["elec"], aggregator_grid)  # creation of a aggregator

    return {"grid": aggregator_grid, "elec": aggregator_elec}


def create_contracts(natures):
    flat_prices_elec = "flat_prices_elec"

    BAU_contract_elec = subclasses_dictionary["Contract"]["FlatEgoistContract"]("BAU_elec", natures["elec"], flat_prices_elec)  # contract for the PV field
    cooperative_contract_elec = subclasses_dictionary["Contract"]["FlatCooperativeContract"]("cooperative_contract_elec", natures["elec"], flat_prices_elec)  # contract for the wind turbine

    return [{"PV": BAU_contract_elec, "WT": cooperative_contract_elec}, {"elec": flat_prices_elec}]


def create_agents():
    PV_producer = Agent("PV_producer")  # the owner of the PV panels

    WT_producer = Agent("WT_producer")  # creation of an agent

    return {"PV": PV_producer, "WT": WT_producer}


def create_devices(world, aggregators, contracts, agents, price_IDs, DSM_proportion, renewable_proportion):
    if renewable_proportion == "low_renewable":
        subclasses_dictionary["Device"]["PV"]("PV_field", contracts['PV'], agents['PV'], aggregators['elec'], "ECOS", "ECOS_field", {"surface": 6700})  # creation of a photovoltaic panel field
        subclasses_dictionary["Device"]["WindTurbine"]("wind_turbine", contracts['WT'], agents['WT'], aggregators['elec'], "ECOS", "ECOS_low")  # creation of a wind turbine

    elif renewable_proportion == "high_renewable":
        subclasses_dictionary["Device"]["PV"]("PV_field", contracts['PV'], agents['PV'], aggregators['elec'], "ECOS", "ECOS_field", {"surface": 20100})  # creation of a photovoltaic panel field
        subclasses_dictionary["Device"]["WindTurbine"]("wind_turbine", contracts['WT'], agents['WT'], aggregators['elec'], "ECOS", "ECOS_high")  # creation of a wind turbine

    elif renewable_proportion == "no_renewable":
        pass  # no renewable energy source is created

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
    world.agent_generation(BAU, "cases/ECOS_TestCases_2020/AgentTemplates/AgentECOS_1_BAU.json", [aggregators["elec"]], {"LVE": price_IDs["elec"]})
    world.agent_generation(BAU * 2, "cases/ECOS_TestCases_2020/AgentTemplates/AgentECOS_2_BAU.json", [aggregators["elec"]], {"LVE": price_IDs["elec"]})
    world.agent_generation(BAU, "cases/ECOS_TestCases_2020/AgentTemplates/AgentECOS_5_BAU.json", [aggregators["elec"]], {"LVE": price_IDs["elec"]})

    # DLC contracts
    world.agent_generation(DLC, "cases/ECOS_TestCases_2020/AgentTemplates/AgentECOS_1_DLC.json", [aggregators["elec"]], {"LVE": price_IDs["elec"]})
    world.agent_generation(DLC * 2, "cases/ECOS_TestCases_2020/AgentTemplates/AgentECOS_2_DLC.json", [aggregators["elec"]], {"LVE": price_IDs["elec"]})
    world.agent_generation(DLC, "cases/ECOS_TestCases_2020/AgentTemplates/AgentECOS_5_DLC.json", [aggregators["elec"]], {"LVE": price_IDs["elec"]})

    # Curtailment contracts
    world.agent_generation(curtailment, "cases/ECOS_TestCases_2020/AgentTemplates/AgentECOS_1_curtailment.json", [aggregators["elec"]], {"LVE": price_IDs["elec"]})
    world.agent_generation(curtailment * 2, "cases/ECOS_TestCases_2020/AgentTemplates/AgentECOS_2_curtailment.json", [aggregators["elec"]], {"LVE": price_IDs["elec"]})
    world.agent_generation(curtailment, "cases/ECOS_TestCases_2020/AgentTemplates/AgentECOS_5_curtailment.json", [aggregators["elec"]], {"LVE": price_IDs["elec"]})


def create_daemons(natures, price_IDs):
    # Price Managers
    # these daemons fix a price for a given nature of energy
    subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("LVE_tariffs", 1, {"nature": natures["elec"].name, "buying_price": [0.12, 0.17], "selling_price": [0.11, 0.11], "hours": [[6, 12], [14, 23]], "identifier": price_IDs["elec"]})  # sets prices for TOU rate

    subclasses_dictionary["Daemon"]["GridPricesDaemon"]("grid_prices_elec", 1, {"nature": natures["elec"].name, "grid_buying_price": 0.2, "grid_selling_price": 0.05})  # sets prices for the system operator

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

    # Wind
    subclasses_dictionary["Daemon"]["WindDaemon"]({"location": "Pau"})


def create_dataloggers(renewable_proportion):
    # datalogger for balances
    # these dataloggers record the balances for each agent, contract, nature and  cluster
    subclasses_dictionary["Datalogger"]["ContractBalanceDatalogger"]()
    subclasses_dictionary["Datalogger"]["AggregatorBalanceDatalogger"]()
    subclasses_dictionary["Datalogger"]["NatureBalanceDatalogger"]()

    subclasses_dictionary["Datalogger"]["ECOSAggregatorDatalogger"]()
    subclasses_dictionary["Datalogger"]["GlobalValuesDatalogger"]()


    # datalogger used to get back producer outputs
    producer_datalogger = Datalogger("producer_datalogger", "ProducerBalances.txt")

    if renewable_proportion != "no_renewable":
        producer_datalogger.add(f"PV_producer.LVE.energy_erased")
        producer_datalogger.add(f"WT_producer.LVE.energy_erased")
        producer_datalogger.add(f"PV_producer.LVE.energy_sold")
        producer_datalogger.add(f"WT_producer.LVE.energy_sold")




