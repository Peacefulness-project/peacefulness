from datetime import datetime

from src.common.World import World
from lib.DefaultNatures.DefaultNatures import *
from src.common.Aggregator import Aggregator
from src.common.Agent import Agent
from src.common.Datalogger import Datalogger

from src.tools.SubclassesDictionary import get_subclasses
subclasses_dictionary = get_subclasses()


def simulation(chosen_strategy, renewable_capacity):
    # ##############################################################################################
    # Initialization
    # ##############################################################################################

    # ##############################################################################################
    # Creation of the world
    # a world <=> a case, it contains all the model
    # a world needs just a name
    name_world = chosen_strategy + "_" + renewable_capacity + "_renewable"
    world = World(name_world)  # creation

    # ##############################################################################################
    # Definition of the path to the files
    pathExport = "cases/Studies/DummySeriesOfCases/Results/" + chosen_strategy + "_" + renewable_capacity + "_renewable"  # directory where results are written
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
    # Natures
    # low voltage electricity
    LVE = load_low_voltage_electricity()

    # low temperature heat
    LTH = load_low_temperature_heat()

    # ##############################################################################################
    # Daemons
    # Price Managers
    # these daemons fix a price for a given nature of energy
    price_managing_daemon_grid = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_grid", {"nature": LTH.name, "buying_price": 0.18, "selling_price": 0.05})  # price manager for the local electrical grid
    price_managing_daemon_elec = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("TOU_prices_elec", {"nature": LVE.name, "buying_price": [0.12, 0.17], "selling_price": [0.11, 0.11], "hours": [[6, 12], [14, 23]]})  # sets prices for TOU rate
    price_managing_daemon_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices_heat", {"nature": LTH.name, "buying_price": 0.1, "selling_price": 0.08})  # sets prices for the system operator

    subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0.18, "limit_selling_price": 0.05})  # sets prices for the system operator
    subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 0.10, "limit_selling_price": 0.08})  # sets prices for the system operator

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
    if chosen_strategy == "strategy_1":
        strategy_elec = subclasses_dictionary["Strategy"]["AlwaysSatisfied"]()
    elif chosen_strategy == "strategy_2":
        strategy_elec = subclasses_dictionary["Strategy"][f"LightAutarkyEmergency"]()

    # the DHN strategy
    strategy_heat = subclasses_dictionary["Strategy"][f"SubaggregatorHeatEmergency"]()

    # the supervisor grid, which always proposes an infinite quantity to sell and to buy
    grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()

    # ##############################################################################################
    # Agents
    national_grid = Agent("national_grid")

    local_electrical_grid_producer = Agent("local_electrical_grid_producer")  # the owner of the PV panels

    DHN_producer = Agent("DHN_producer")  # the owner of the district heating network

    # ##############################################################################################
    # Contracts
    contract_grid = subclasses_dictionary["Contract"]["EgoistContract"]("elec_grid", LVE, price_managing_daemon_grid)

    contract_elec = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_elec", LVE, price_managing_daemon_elec)

    contract_heat = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_heat", LTH, price_managing_daemon_heat)

    # ##############################################################################################
    # Aggregators

    # the first aggregator represents the national electrical grid
    aggregator_name = "Enedis"
    aggregator_grid = Aggregator(aggregator_name, LVE, grid_strategy, national_grid)

    # here we create a second one put under the orders of the first
    aggregator_name = "general_aggregator"
    aggregator_elec = Aggregator(aggregator_name, LVE, strategy_elec, local_electrical_grid_producer, aggregator_grid, contract_grid)  # creation of a aggregator

    # here we create another aggregator dedicated to heat
    aggregator_name = "Local_DHN"
    aggregator_heat = Aggregator(aggregator_name, LTH, strategy_heat, DHN_producer, aggregator_elec, contract_elec, 3.6, 2000)  # creation of a aggregator

    # ##############################################################################################
    # Devices

    if renewable_capacity == "little":
        subclasses_dictionary["Device"]["PV"]("PV_field", contract_elec, local_electrical_grid_producer, aggregator_elec, "ECOS", "ECOS_field", {"surface": 1000, "location": "Pau"})  # creation of a photovoltaic panel field
    elif renewable_capacity == "a_lot":
        subclasses_dictionary["Device"]["PV"]("PV_field", contract_elec, local_electrical_grid_producer, aggregator_elec, "ECOS", "ECOS_field", {"surface": 3000, "location": "Pau"})  # creation of a photovoltaic panel field

    subclasses_dictionary["Device"]["DummyProducer"]("heat_production", contract_heat, DHN_producer, aggregator_heat, "ECOS", "ECOS")  # creation of a heat production unit

    # DLC contracts
    world.agent_generation(1000, "cases/Studies/DummySeriesOfCases/AgentTemplates/dummy_agent_template.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_daemon_elec, "LTH": price_managing_daemon_heat})

    # ##############################################################################################
    # Dataloggers

    # datalogger for balances
    # these dataloggers record the balances for each agent, contract, nature and  cluster
    subclasses_dictionary["Datalogger"]["ContractBalancesDatalogger"]()
    subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"]()
    subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"]()

    subclasses_dictionary["Datalogger"]["ECOSAggregatorDatalogger"]()
    subclasses_dictionary["Datalogger"]["MismatchDatalogger"]()

    # datalogger used to get back producer outputs
    producer_datalogger = Datalogger("producer_datalogger", "ProducerBalances.txt")

    producer_datalogger.add(f"{local_electrical_grid_producer.name}.{LVE.name}.energy_erased")
    producer_datalogger.add(f"{DHN_producer.name}.{LTH.name}.energy_erased")
    producer_datalogger.add(f"{local_electrical_grid_producer.name}.{LVE.name}.energy_sold")
    producer_datalogger.add(f"{DHN_producer.name}.{LTH.name}.energy_sold")

    # ##############################################################################################
    # Simulation
    # ##############################################################################################
    world.start()




