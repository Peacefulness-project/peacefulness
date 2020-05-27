from datetime import datetime

from src.common.World import World
from lib.DefaultNatures.DefaultNatures import load_low_voltage_electricity
from src.common.Aggregator import Aggregator
from src.common.Agent import Agent
from src.common.Datalogger import Datalogger

from src.tools.SubclassesDictionary import get_subclasses
subclasses_dictionary = get_subclasses()


def simulation(exchange_strategy, distribution_strategy, renewable_proportion, DSM_proportion):
    # ##############################################################################################
    # Initialization
    # ##############################################################################################

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

    # ##############################################################################################
    # Model creation
    # ##############################################################################################

    # ##############################################################################################
    # Strategies
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

    # ##############################################################################################
    # Natures
    # low voltage electricity
    LVE = load_low_voltage_electricity()

    # ##############################################################################################
    # Daemons
    # Price Managers
    # these daemons fix a price for a given nature of energy
    price_managing_elec = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("TOU_price_managing", {"nature": LVE.name, "buying_price": [0.12, 0.17], "selling_price": [0.11, 0.11], "hours": [[6, 12], [14, 23]]})  # sets prices for TOU rate

    price_managing_daemon_grid = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_grid", {"nature": LVE.name, "buying_price": 0.2, "selling_price": 0.05})  # price manager for the local electrical grid
    subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0.2, "limit_selling_price": 0.05})  # sets prices for the system operator

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

    # Wind
    subclasses_dictionary["Daemon"]["WindDaemon"]({"location": "Pau"})

    # ##############################################################################################
    # Agents
    PV_producer = Agent("PV_producer")  # the owner of the PV panels

    WT_producer = Agent("WT_producer")  # creation of an agent

    local_electrical_grid = Agent("local_electrical_grid_producer")

    national_grid = Agent("national_grid")

    # ##############################################################################################
    # Contracts
    BAU_contract_elec = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_elec", LVE, price_managing_daemon_grid)  # contract for the PV field

    cooperative_contract_elec = subclasses_dictionary["Contract"]["CooperativeContract"]("cooperative_contract_elec", LVE, price_managing_elec)  # contract for the wind turbine

    contract_grid = subclasses_dictionary["Contract"]["EgoistContract"]("elec_grid", LVE, price_managing_daemon_grid)

    # ##############################################################################################
    # Aggregators
    # and then we create a third who represents the grid
    aggregator_name = "Enedis"
    aggregator_grid = Aggregator(aggregator_name, LVE, grid_supervisor, national_grid)

    # here we create a second one put under the orders of the first
    aggregator_name = "general_aggregator"
    aggregator_elec = Aggregator(aggregator_name,  LVE, supervisor_elec, local_electrical_grid, aggregator_grid, contract_grid)  # creation of a aggregator

    # ##############################################################################################
    # Devices
    if renewable_proportion == "low_renewable":
        subclasses_dictionary["Device"]["PV"]("PV_field", BAU_contract_elec, PV_producer, aggregator_elec, "ECOS", "ECOS_field", {"surface": 6700, "location": "Pau"})  # creation of a photovoltaic panel field
        subclasses_dictionary["Device"]["WindTurbine"]("wind_turbine", cooperative_contract_elec, WT_producer, aggregator_elec, "ECOS", "ECOS_low", {"location": "Pau"})  # creation of a wind turbine

    elif renewable_proportion == "high_renewable":
        subclasses_dictionary["Device"]["PV"]("PV_field", BAU_contract_elec, PV_producer, aggregator_elec, "ECOS", "ECOS_field", {"surface": 20100, "location": "Pau"})  # creation of a photovoltaic panel field
        subclasses_dictionary["Device"]["WindTurbine"]("wind_turbine", cooperative_contract_elec, WT_producer, aggregator_elec, "ECOS", "ECOS_high", {"location": "Pau"})  # creation of a wind turbine

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
    world.agent_generation(BAU, "cases/ECOS_TestCases_2020/AgentTemplates/AgentECOS_1_BAU.json", [aggregator_elec], {"LVE": price_managing_elec})
    world.agent_generation(BAU * 2, "cases/ECOS_TestCases_2020/AgentTemplates/AgentECOS_2_BAU.json", [aggregator_elec], {"LVE": price_managing_elec})
    world.agent_generation(BAU, "cases/ECOS_TestCases_2020/AgentTemplates/AgentECOS_5_BAU.json", [aggregator_elec], {"LVE": price_managing_elec})

    # DLC contracts
    world.agent_generation(DLC, "cases/ECOS_TestCases_2020/AgentTemplates/AgentECOS_1_DLC.json", [aggregator_elec], {"LVE": price_managing_elec})
    world.agent_generation(DLC * 2, "cases/ECOS_TestCases_2020/AgentTemplates/AgentECOS_2_DLC.json", [aggregator_elec], {"LVE": price_managing_elec})
    world.agent_generation(DLC, "cases/ECOS_TestCases_2020/AgentTemplates/AgentECOS_5_DLC.json", [aggregator_elec], {"LVE": price_managing_elec})

    # Curtailment contracts
    world.agent_generation(curtailment, "cases/ECOS_TestCases_2020/AgentTemplates/AgentECOS_1_curtailment.json", [aggregator_elec], {"LVE": price_managing_elec})
    world.agent_generation(curtailment * 2, "cases/ECOS_TestCases_2020/AgentTemplates/AgentECOS_2_curtailment.json", [aggregator_elec], {"LVE": price_managing_elec})
    world.agent_generation(curtailment, "cases/ECOS_TestCases_2020/AgentTemplates/AgentECOS_5_curtailment.json", [aggregator_elec], {"LVE": price_managing_elec})

    # ##############################################################################################
    # Dataloggers
    # datalogger for balances
    # these dataloggers record the balances for each agent, contract, nature and  cluster
    subclasses_dictionary["Datalogger"]["ContractBalancesDatalogger"]()
    subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"]()
    subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"]()

    subclasses_dictionary["Datalogger"]["ECOSAggregatorDatalogger"]()
    subclasses_dictionary["Datalogger"]["GlobalValuesDatalogger"]()


    # datalogger used to get back producer outputs
    producer_datalogger = Datalogger("producer_datalogger", "ProducerBalances.txt")

    if renewable_proportion != "no_renewable":
        producer_datalogger.add(f"PV_producer.LVE.energy_erased")
        producer_datalogger.add(f"WT_producer.LVE.energy_erased")
        producer_datalogger.add(f"PV_producer.LVE.energy_sold")
        producer_datalogger.add(f"WT_producer.LVE.energy_sold")

    # ##############################################################################################
    # Simulation
    # ##############################################################################################
    world.start()

