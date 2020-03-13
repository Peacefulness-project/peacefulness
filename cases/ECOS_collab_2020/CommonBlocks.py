from datetime import datetime

from src.common.World import World
from src.common.Nature import Nature
from src.common.Aggregator import Aggregator
from src.common.Agent import Agent
from src.common.Datalogger import Datalogger

from src.tools.SubclassesDictionary import get_subclasses
subclasses_dictionary = get_subclasses()


def create_world_with_set_parameters(strategy, DSM_proportion):

    # ##############################################################################################
    # Creation of the world
    # a world <=> a case, it contains all the model
    # a world needs just a name
    name_world = "ECOS_collab_2020"
    world = World(name_world)  # creation

    # ##############################################################################################
    # Definition of the path to the files
    pathExport = "cases/Edwin_profiles/Results/" + strategy + "_" + DSM_proportion  # directory where results are written
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


def create_strategies(world, strategy):
    # the local electrical grid strategy
    description = "Depends on the case"
    name_supervisor = "elec_supervisor"
    supervisor_elec = subclasses_dictionary[f"{strategy}Emergency"](world, name_supervisor, description)

    # the DHN strategy
    description = "Depends on the case"
    name_supervisor = "heat_supervisor"
    supervisor_heat = subclasses_dictionary[f"SubaggregatorHeatEmergency"](world, name_supervisor, description)

    # the national grid strategy
    description = "this supervisor represents the ISO. Here, we consider that it has an infinite capacity to give or to accept energy"
    name_supervisor = "benevolent_operator"
    grid_supervisor = subclasses_dictionary["Grid"](world, name_supervisor, description)

    return {"elec": supervisor_elec, "heat": supervisor_heat, "grid": grid_supervisor}


def create_natures(world):
    nature_name = "LVE"
    nature_description = "Low Voltage Electricity"
    elec = Nature(world, nature_name, nature_description)  # creation of a nature

    nature_name = "Heat"
    nature_description = "Energy transported by a district heating network"
    heat = Nature(world, nature_name, nature_description)  # creation of a nature

    return {"elec": elec, "heat": heat}


def create_aggregators(world, natures, strategies):
    # and then we create a third who represents the grid
    aggregator_name = "Enedis"
    aggregator_grid = Aggregator(world, aggregator_name, natures["elec"], strategies["grid"])

    # here we create a second one put under the orders of the first
    aggregator_name = "general_aggregator"
    aggregator_elec = Aggregator(world, aggregator_name,  natures["elec"], strategies["elec"], aggregator_grid)  # creation of a aggregator

    # here we create another aggregator dedicated to heat
    aggregator_name = "Local_DHN"
    aggregator_heat = Aggregator(world, aggregator_name,  natures["heat"], strategies["heat"], aggregator_grid)  # creation of a aggregator

    return {"grid": aggregator_grid, "elec": aggregator_elec, "heat": aggregator_heat}


def create_contracts(world, natures):
    flat_prices_elec = "flat_prices_elec"
    contract_elec = subclasses_dictionary["FlatEgoistContract"](world, "BAU_elec", natures["elec"], flat_prices_elec)

    flat_prices_heat = "flat_prices_heat"
    contract_heat = subclasses_dictionary["FlatEgoistContract"](world, "BAU_heat", natures["heat"], flat_prices_heat)

    return [{"elec": contract_elec, "heat": contract_heat}, {"elec": flat_prices_elec, "heat": flat_prices_heat}]


def create_agents(world):
    PV_producer = Agent(world, "PV_producer")  # the owner of the PV panels

    solar_thermal_producer = Agent(world, "solar_thermal_producer")  # the owner of the solar thermal collectors

    return {"elec":PV_producer, "heat":solar_thermal_producer}


def create_devices(world, aggregators, contracts, agents, price_IDs, DSM_proportion, sizing):
    if sizing == "mean":
        sizing_coeff_elec = 1
        sizing_coeff_heat = 1
    elif sizing == "peak":
        sizing_coeff_elec = 54000/18000
        sizing_coeff_heat = 23550/9350

    subclasses_dictionary["PV"](world, "PV_field", contracts['elec'], agents['elec'], aggregators['elec'], "ECOS", "ECOS_field", {"surface": 18000 * sizing_coeff_elec})  # creation of a photovoltaic panel field

    subclasses_dictionary["SolarThermalCollector"](world, "solar_thermal_collector_field", contracts['heat'], agents['heat'], aggregators['heat'], "ECOS", "ECOS_field", {"surface": 9350 * sizing_coeff_heat})  # creation of a solar thermal collector

    if DSM_proportion == "high":
        BAU = 165
        DLC = 200
        curtailment = 135
    elif DSM_proportion == "low":
        BAU = 335
        DLC = 100
        curtailment = 65
    elif DSM_proportion == "no":
        BAU = 500
        DLC = 0
        curtailment = 0

    # BAU contracts
    world.agent_generation(BAU, "cases/ECOS_collab_2020/AgentTemplates/AgentECOS_1_BAU.json", [aggregators["elec"], aggregators["heat"]], {"LVE": price_IDs["elec"], "Heat": price_IDs["heat"]})
    world.agent_generation(BAU * 2, "cases/ECOS_collab_2020/AgentTemplates/AgentECOS_2_BAU.json", [aggregators["elec"], aggregators["heat"]], {"LVE": price_IDs["elec"], "Heat": price_IDs["heat"]})
    world.agent_generation(BAU, "cases/ECOS_collab_2020/AgentTemplates/AgentECOS_5_BAU.json", [aggregators["elec"], aggregators["heat"]], {"LVE": price_IDs["elec"], "Heat": price_IDs["heat"]})

    # DLC contracts
    world.agent_generation(DLC, "cases/ECOS_collab_2020/AgentTemplates/AgentECOS_1_DLC.json", [aggregators["elec"], aggregators["heat"]], {"LVE": price_IDs["elec"], "Heat": price_IDs["heat"]})
    world.agent_generation(DLC * 2, "cases/ECOS_collab_2020/AgentTemplates/AgentECOS_2_DLC.json", [aggregators["elec"], aggregators["heat"]], {"LVE": price_IDs["elec"], "Heat": price_IDs["heat"]})
    world.agent_generation(DLC, "cases/ECOS_collab_2020/AgentTemplates/AgentECOS_5_DLC.json", [aggregators["elec"], aggregators["heat"]], {"LVE": price_IDs["elec"], "Heat": price_IDs["heat"]})

    # Curtailment contracts
    world.agent_generation(curtailment, "cases/ECOS_collab_2020/AgentTemplates/AgentECOS_1_curtailment.json", [aggregators["elec"], aggregators["heat"]], {"LVE": price_IDs["elec"], "Heat": price_IDs["heat"]})
    world.agent_generation(curtailment * 2, "cases/ECOS_collab_2020/AgentTemplates/AgentECOS_2_curtailment.json", [aggregators["elec"], aggregators["heat"]], {"LVE": price_IDs["elec"], "Heat": price_IDs["heat"]})
    world.agent_generation(curtailment, "cases/ECOS_collab_2020/AgentTemplates/AgentECOS_5_curtailment.json", [aggregators["elec"], aggregators["heat"]], {"LVE": price_IDs["elec"], "Heat": price_IDs["heat"]})


def create_daemons(world, natures, price_IDs):
    # Price Managers
    # these daemons fix a price for a given nature of energy
    subclasses_dictionary["PriceManagerTOUDaemon"](world, "LVE_tariffs", 1, {"nature": natures["elec"].name, "buying_price": [0.2125, 0.15], "selling_price": [0, 0], "hours": [[6, 12], [14, 23]], "identifier": price_IDs["elec"]})  # sets prices for TOU rate
    subclasses_dictionary["PriceManagerDaemon"](world, "Heat_tariffs", 1, {"nature": natures["heat"].name, "buying_price": 0.1, "selling_price": 0.08, "identifier": price_IDs["heat"]})  # sets prices for the system operator

    subclasses_dictionary["GridPricesDaemon"](world, "grid_prices_elec", 1, {"nature": natures["elec"].name, "grid_buying_price": 0.2, "grid_selling_price": 0.05})  # sets prices for the system operator
    subclasses_dictionary["GridPricesDaemon"](world, "grid_prices_heat", 1, {"nature": natures["heat"].name, "grid_buying_price": 0.15, "grid_selling_price": 0.1})  # sets prices for the system operator

    # Outdoor temperature
    # this daemon is responsible for the value of outdoor temperature in the catalog
    subclasses_dictionary["OutdoorTemperatureDaemon"](world, "Azzie", {"location": "Pau"})

    # Indoor temperature
    # this daemon is responsible for the value of indoor temperatures in the catalog
    subclasses_dictionary["IndoorTemperatureDaemon"](world, "Asie")

    # Water temperature
    # this daemon is responsible for the value of the water temperature in the catalog
    subclasses_dictionary["ColdWaterDaemon"](world, "Mephisto", {"location": "Pau"})

    # Irradiation
    # this daemon is responsible for updating the value of raw solar irradiation
    subclasses_dictionary["IrradiationDaemon"](world, "toto", {"location": "Pau"})


def create_dataloggers(world):
    # datalogger for balances
    # these dataloggers record the balances for each agent, contract, nature and  cluster
    subclasses_dictionary["ContractBalanceDatalogger"](world)
    subclasses_dictionary["AggregatorBalanceDatalogger"](world)
    subclasses_dictionary["NatureBalanceDatalogger"](world)

    subclasses_dictionary["ECOSAggregatorDatalogger"](world)
    subclasses_dictionary["GlobalValuesDatalogger"](world)


    # datalogger used to get back producer outputs
    producer_datalogger = Datalogger(world, "producer_datalogger", "ProducerBalances.txt")

    producer_datalogger.add(f"PV_producer.LVE.energy_erased")
    producer_datalogger.add(f"solar_thermal_producer.Heat.energy_erased")
    producer_datalogger.add(f"PV_producer.LVE.energy_sold")
    producer_datalogger.add(f"solar_thermal_producer.Heat.energy_sold")

    producer_datalogger.add(f"PV_field_exergy_in")
    producer_datalogger.add(f"solar_thermal_collector_field_exergy_in")
    producer_datalogger.add(f"PV_field_exergy_out")
    producer_datalogger.add(f"solar_thermal_collector_field_exergy_out")


