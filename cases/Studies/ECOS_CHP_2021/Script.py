
from datetime import datetime

from src.common.World import World
from lib.DefaultNatures.DefaultNatures import load_low_voltage_electricity, load_low_temperature_heat, load_low_pressure_gas
from src.common.Aggregator import Aggregator
from src.common.Agent import Agent
from src.common.Datalogger import Datalogger

from src.tools.SubclassesDictionary import get_subclasses
subclasses_dictionary = get_subclasses()


def simulation(DSM_proportion, sizing):
    # ##############################################################################################
    # Settings
    # ##############################################################################################

    # ##############################################################################################
    # Creation of the world
    # a world <=> a case, it contains all the model
    # a world needs just a name
    name_world = "ECOS_CHP_2021"
    world = World(name_world)  # creation

    # ##############################################################################################
    # Definition of the path to the files
    pathExport = "cases/Studies/ECOS_CHP_2021/Results/" + "_" + DSM_proportion + "_" + sizing  # directory where results are written
    world.set_directory(pathExport)  # registration

    # ##############################################################################################
    # Definition of the random seed to be used
    # The default seed is the current time (the value returned by datetime.now())
    world.set_random_seed("sunflower")

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
    # Natures
    # low voltage electricity
    LVE = load_low_voltage_electricity()

    # low temperature heat
    LTH = load_low_temperature_heat()

    # low pressure gas
    LPG = load_low_pressure_gas()

    # ##############################################################################################
    # Daemons
    # Price Managers
    # these daemons fix a price for a given nature of energy
    if sizing == "ittle":
        price_managing_elec = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("TOU_prices_elec", {"nature": LVE.name, "buying_price": [, ], "selling_price": [0.245, 0.245], "hours": [[6, 12], [14, 23]]})  # sets prices for TOU rate
        price_managing_daemon_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_heat", {"nature": LTH.name, "buying_price": , "selling_price": 0})  # price manager for the local electrical grid

        price_managing_daemon_DHN = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_DHN", {"nature": LTH.name, "buying_price": , "selling_price": 0})  # price manager for the local electrical grid
        subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 0.407, "limit_selling_price": 0})  # sets prices for the system operator
        price_managing_daemon_CHP_gas = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_CHP_gas", {"nature": LPG.name, "buying_price": , "selling_price": 0})  # price manager for the local electrical grid
        price_managing_daemon_CHP_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_CHP_heat", {"nature": LTH.name, "buying_price": 0, "selling_price": })  # price manager for the local electrical grid
        price_managing_daemon_CHP_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_CHP_elec", {"nature": LVE.name, "buying_price": 0, "selling_price": })  # price manager for the local electrical grid

    elif sizing == "large":
        price_managing_elec = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("TOU_prices_elec", {"nature": LVE.name, "buying_price": [, ], "selling_price": [, ], "hours": [[6, 12], [14, 23]]})  # sets prices for TOU rate
        price_managing_daemon_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_heat", {"nature": LTH.name, "buying_price": , "selling_price": 0})  # price manager for the local electrical grid

        price_managing_daemon_DHN = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_DHN", {"nature": LTH.name, "buying_price": , "selling_price": 0})  # price manager for the local electrical grid
        price_managing_daemon_CHP_gas = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_CHP_gas", {"nature": LPG.name, "buying_price": , "selling_price": 0})  # price manager for the local electrical grid
        price_managing_daemon_CHP_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_CHP_heat", {"nature": LTH.name, "buying_price": 0, "selling_price": })  # price manager for the local electrical grid
        price_managing_daemon_CHP_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_CHP_elec", {"nature": LVE.name, "buying_price": 0, "selling_price": })  # price manager for the local electrical grid


    subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": , "limit_selling_price": })  # sets prices for the system operator

    price_managing_daemon_grid = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_grid", {"nature": LVE.name, "buying_price": , "selling_price": })  # price manager for the local electrical grid
    subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": , "limit_selling_price": })  # sets prices for the system operator

    # Outdoor temperature
    # this daemon is responsible for the value of outdoor temperature in the catalog
    subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Pau"})

    # Indoor temperature
    # this daemon is responsible for the value of indoor temperatures in the catalog
    subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

    # Water temperature
    # this daemon is responsible for the value of the water temperature in the catalog
    subclasses_dictionary["Daemon"]["ColdWaterTemperatureDaemon"]({"location": "Pau"})

    # Irradiation
    # this daemon is responsible for updating the value of raw solar irradiation
    subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Pau"})

    # ##############################################################################################
    # Strategies

    # the local electrical grid strategy
    supervisor_elec = subclasses_dictionary["Strategy"][f"LightAutarkyEmergency"]()

    # the DHN strategy
    supervisor_heat = subclasses_dictionary["Strategy"][f"SubaggregatorHeatEmergency"]()

    # the national grid strategy
    grid_supervisor = subclasses_dictionary["Strategy"]["Grid"]()

    # ##############################################################################################
    # Agents

    CHP_producer = Agent("CHP_producer")  # the owner of the solar thermal collectors

    national_grid = Agent("national_grid")

    local_electrical_grid_manager = Agent("local_electrical_grid_producer")  # the owner of the Photovoltaics panels

    DHN_manager = Agent("DHN_producer")  # the owner of the district heating network

    # ##############################################################################################
    # Contracts

    # contracts for aggregators
    contract_grid = subclasses_dictionary["Contract"]["EgoistContract"]("elec_grid", LVE, price_managing_daemon_grid)

    contract_DHN = subclasses_dictionary["Contract"]["EgoistContract"]("DHN_grid", LTH, price_managing_daemon_DHN)

    # contracts for the CHP unit
    contract_CHP_heat = subclasses_dictionary["Contract"]["EgoistContract"]("CHP_heat", LTH, price_managing_daemon_CHP_heat)

    contract_CHP_elec = subclasses_dictionary["Contract"]["EgoistContract"]("CHP_elec", LVE, price_managing_daemon_CHP_elec)

    contract_CHP_gas = subclasses_dictionary["Contract"]["EgoistContract"]("CHP_gas", LPG, price_managing_daemon_CHP_gas)


    # ##############################################################################################
    # Aggregators
    # national electrical grid
    aggregator_name = "elec_grid"
    aggregator_grid = Aggregator(aggregator_name, LVE, grid_supervisor, national_grid)

    # gas grid
    aggregator_name = "gas_grid"
    aggregator_gas = Aggregator(aggregator_name, LPG, grid_supervisor, national_grid)

    # local electrical aggregator
    aggregator_name = "general_aggregator"
    aggregator_elec = Aggregator(aggregator_name, LVE, supervisor_elec, local_electrical_grid_manager, aggregator_grid, contract_grid)  # creation of a aggregator

    # DHN aggregator
    aggregator_name = "Local_DHN"
    aggregator_heat = Aggregator(aggregator_name, LTH, supervisor_heat, DHN_manager, aggregator_elec, contract_DHN, 3.6, 3344)  # creation of a aggregator

    # ##############################################################################################
    # Devices
    if sizing == "little":
        CHP_max_power =
    elif sizing == "large":
        CHP_max_power =

    subclasses_dictionary["Devices"]["CombinedHeatAndPower"]("heat_plant", [contract_CHP_elec, contract_CHP_gas, contract_CHP_heat], CHP_producer, aggregator_gas, [aggregator_heat, aggregator_elec], {"device": "standard"}, {"max_power": CHP_max_power})

    # repartition of contracts according to the chosen proportion
    if DSM_proportion == "high_DSM":
        BAU =
        DLC =
        curtailment =
    elif DSM_proportion == "low_DSM":
        BAU =
        DLC =
        curtailment =
    elif DSM_proportion == "no_DSM":
        BAU =
        DLC = 0
        curtailment = 0

    # BAU contracts
    world.agent_generation(BAU, "cases/Studies/ECOS_CHP_2021/AgentTemplates/AgentECOS_1_BAU.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_daemon_heat})
    world.agent_generation(BAU, "cases/Studies/ECOS_CHP_2021/AgentTemplates/AgentECOS_2_BAU.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_daemon_heat})
    world.agent_generation(BAU, "cases/Studies/ECOS_CHP_2021/AgentTemplates/Agent_5_p_BAU_no_PV.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_daemon_heat})

    # DLC contracts
    world.agent_generation(DLC, "cases/Studies/ECOS_CHP_2021/AgentTemplates/AgentECOS_1_DLC.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_daemon_heat})
    world.agent_generation(DLC, "cases/Studies/ECOS_CHP_2021/AgentTemplates/AgentECOS_2_DLC.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_daemon_heat})
    world.agent_generation(DLC, "cases/Studies/ECOS_CHP_2021/AgentTemplates/AgentECOS_5_DLC.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_daemon_heat})

    # Curtailment contracts
    world.agent_generation(curtailment, "cases/Studies/ECOS_CHP_2021/AgentTemplates/AgentECOS_1_curtailment.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_daemon_heat})
    world.agent_generation(curtailment, "cases/Studies/ECOS_CHP_2021/AgentTemplates/AgentECOS_2_curtailment.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_daemon_heat})
    world.agent_generation(curtailment, "cases/Studies/ECOS_CHP_2021/AgentTemplates/Agent_5_curtailment_no_PV.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_daemon_heat})

    # ##############################################################################################
    # Dataloggers
    # datalogger for balances
    # these dataloggers record the balances for each agent, contract, nature and  cluster
    subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"](period="global")
    subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"](period="global")
    subclasses_dictionary["Datalogger"]["MismatchDatalogger"](period="global")

    subclasses_dictionary["Datalogger"]["WeightedSelfSufficiencyDatalogger"](period="global")
    subclasses_dictionary["Datalogger"]["SelfSufficiencyDatalogger"]()

    # ##############################################################################################
    # Simulation
    # ##############################################################################################
    world.start()


