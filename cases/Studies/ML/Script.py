# This script is the one deconstructed in the tuto to create a case on the wiki.


# ##############################################################################################
# Importations
from datetime import datetime

from src.common.World import World

from src.common.Nature import Nature

# pre-defined natures
from lib.DefaultNatures.DefaultNatures import *

from src.common.Agent import Agent

from src.common.Aggregator import Aggregator

from src.common.Datalogger import Datalogger

# all the subclasses are imported in the following dictionary
from src.tools.SubclassesDictionary import get_subclasses


def run_simulation(start_date, hours_simulated, priorities_conso, priorities_prod):

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
    name_world = "Disc World"
    world = World(name_world)  # creation

    # ##############################################################################################
    # Definition of the path to the files
    pathExport = "cases/Studies/ML/Results"
    world.set_directory(pathExport)  # registration

    # ##############################################################################################
    # Definition of the random seed
    # The default seed is the current time (the value returned by datetime.now())
    world.set_random_seed("sunflower")

    # ##############################################################################################
    # Time parameters
    # it needs a start date, the value of an iteration in hours and the total number of iterations
    # start_date = datetime(year=2018, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)  # a start date in the datetime format
    world.set_time(start_date,  # time management: start date
                   1,  # value of a time step (in hours)
                   hours_simulated)  # number of time steps simulated

    # ##############################################################################################
    # Model
    # ##############################################################################################

    # ##############################################################################################
    # Creation of nature

    # low voltage electricity
    LVE = load_low_voltage_electricity()

    # ##############################################################################################
    # Creation of daemons

    # Price Managers
    # this daemons fix a price for a given nature of energy
    price_manager_elec = subclasses_dictionary["Daemon"]["PriceManagerRTPDaemon"]("prices_elec", {"location": "France", "coefficient": 1/3}, "cases/Studies/ML/data/prices.json")  # sets prices for TOU rate

    # price_manager_grid = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("grid_prices", {"nature": LVE.name, "buying_price": 0.2, "selling_price": 0.05})  # sets prices for TOU rate

    # limit prices
    # the following daemons fix the maximum and minimum price at which energy can be exchanged
    limit_prices_elec_grid = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0.2, "limit_selling_price": 0.05})  # sets limit price accepted

    # Indoor temperature
    # this daemon is responsible for the value of indoor temperatures in the catalog
    indoor_temperature_daemon = subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

    # Outdoor temperature
    # this daemon is responsible for the value of outside temperature in the catalog
    outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Santerre"}, filename="cases/Studies/ML/data/temperature.json", exergy=False)

    # Water temperature
    # this daemon is responsible for the value of the water temperature in the catalog
    water_temperature_daemon = subclasses_dictionary["Daemon"]["ColdWaterTemperatureDaemon"]({"location": "France"})

    # Irradiation
    # this daemon is responsible for updating the value of raw solar irradiation
    irradiation_daemon = subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Santerre"}, filename="cases/Studies/ML/data/irradiation.json", direct_normal_irradiation=False)

    # Wind
    # this daemon is responsible for updating the value of raw solar Wind
    wind_daemon = subclasses_dictionary["Daemon"]["WindSpeedDaemon"]({"location": "Santerre"}, filename="cases/Studies/ML/data/wind_speed.json")

    # Water flow
    # this daemon is responsible for updating the value of the flow of water for an electric dam
    water_flow_daemon = subclasses_dictionary["Daemon"]["WaterFlowDaemon"]({"location": "GavedePau_Pau"})

    # ##############################################################################################
    # Creation of strategies

    # the BAU strategy
    strategy_elec = subclasses_dictionary["Strategy"]["TrainingStrategy"](priorities_conso, priorities_prod)

    # the strategy grid, which always proposes an infinite quantity to sell and to buy
    grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()

    # ##############################################################################################
    # Manual creation of agents

    # the first block corresponds to the producers

    battery_owner = Agent("storer")  # creation of an agent
    producer = Agent("producer")  # creation of an agent

    # the second block corresponds to the grid managers (i.e the owners of the aggregators)
    grid_manager = Agent("grid_manager")  # creation of an agent

    local_electrical_grid = Agent("local_electrical_grid")  # creation of an agent

    # ##############################################################################################
    # Manual creation of contracts

    # producers
    BAU_elec = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_elec", LVE, price_manager_elec)

    cooperative_contract_elec = subclasses_dictionary["Contract"]["CooperativeContract"]("cooperative_contract_elec", LVE, price_manager_elec)  # a contract

    contract_grid = subclasses_dictionary["Contract"]["EgoistContract"]("grid_prices_manager", LVE, price_manager_elec)  # this contract is the one between the local electrical grid and the national one

    # ##############################################################################################
    # Creation of aggregators

    # we create a first aggregator who represents the national electrical grid
    aggregator_name = "Enedis"
    aggregator_grid = Aggregator(aggregator_name, LVE, grid_strategy, grid_manager)

    # here we create a second one put under the orders of the first
    aggregator_name = "general_aggregator"
    aggregator_elec = Aggregator(aggregator_name, LVE, strategy_elec, local_electrical_grid, aggregator_grid, contract_grid, capacity={"buying": 1500, "selling": 1500})  # creation of a aggregator

    # ##############################################################################################
    # Manual creation of devices

    battery = subclasses_dictionary["Device"]["ElectricalBattery"]("battery", cooperative_contract_elec, battery_owner, aggregator_elec, {"device": "domestic_battery"}, {"capacity": 1000})  # creation of a wind turbine
    subclasses_dictionary["Device"]["ElectricDam"]("electric_dam", cooperative_contract_elec, producer, aggregator_elec, {"device": "Pelton"}, {"height": 5, "max_power": 3000, "water_flow_daemon": water_flow_daemon.name})  # creation of an electric dam
    subclasses_dictionary["Device"]["WindTurbine"]("wind_turbine_1", BAU_elec, producer, aggregator_elec, {"device": "little"}, {"wind_speed_daemon": wind_daemon.name})  # creation of a wind turbine

    # ##############################################################################################
    # Automated generation of complete agents (i.e with devices and contracts)

    # BAU contracts
    world.agent_generation("M5BAU", 50, "cases/Studies/ML/agent_templates/Agent_5_BAU.json", aggregator_elec, {"LVE": price_manager_elec}, {"irradiation_daemon": irradiation_daemon, "outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": water_temperature_daemon})

    # DLC contracts
    world.agent_generation("M5Coop", 50, "cases/Studies/ML/agent_templates/Agent_5_DLC.json", aggregator_elec, {"LVE": price_manager_elec}, {"irradiation_daemon": irradiation_daemon, "outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": water_temperature_daemon})

    # Curtailment contracts
    world.agent_generation("M5Curt", 50, "cases/Studies/ML/agent_templates/Agent_5_curtailment.json", aggregator_elec, {"LVE": price_manager_elec}, {"irradiation_daemon": irradiation_daemon, "outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": water_temperature_daemon})

    # ##############################################################################################
    # Creation of dataloggers

    # datalogger used to get back producer outputs
    producer_datalogger = Datalogger("performances_evaluation", "PerformancesEvaluation.txt")

    # datalogger for balances
    # these dataloggers record the balances for each agent, contract, nature and  cluster
    subclasses_dictionary["Datalogger"]["ClusteringMetricsDatalogger"](period=1)
    subclasses_dictionary["Datalogger"]["SelfSufficiencyDatalogger"](period=1)
    subclasses_dictionary["Datalogger"]["CurtailmentDatalogger"](period=1)
    subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"](period=1)

    # ##############################################################################################
    # Simulation start
    world.start()

    # ##############################################################################################
    # output sent to ML algorithm
    return world.catalog



