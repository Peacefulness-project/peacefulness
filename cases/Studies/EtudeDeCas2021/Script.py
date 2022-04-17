
from datetime import datetime
from math import inf

from src.common.World import World
from lib.DefaultNatures.DefaultNatures import load_low_voltage_electricity, load_low_temperature_heat, load_low_pressure_gas
from src.common.Aggregator import Aggregator
from src.common.Agent import Agent
from src.common.Datalogger import Datalogger
from src.tools.GraphAndTex import GraphOptions

from src.tools.SubclassesDictionary import get_subclasses
subclasses_dictionary = get_subclasses()


def simulation(DSM_proportion, strategy_exchange, strategy_distribution, grid):
    # ##############################################################################################
    # Settings
    # ##############################################################################################

    # ##############################################################################################
    # Creation of the world
    # a world <=> a case, it contains all the model
    # a world needs just a name
    name_world = "etude_de_cas_2021_" + str(DSM_proportion) + "_" + strategy_exchange + "_" + strategy_distribution + "_" + grid
    world = World(name_world)  # creation

    # ##############################################################################################
    # Definition of the path to the files
    pathExport = "cases/Studies/EtudeDeCas2021/Results/" + str(DSM_proportion) + "_" + strategy_exchange + "_" + strategy_distribution + "_" + grid  # directory where results are written
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

    # ##############################################################################################
    # Daemons
    # Price Managers
    # these daemons fix a price for a given nature of energy

    # price managers
    if grid == "mixed":
        price_managing_heat_BAU = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_heat_BAU", {"nature": LTH.name, "buying_price": 0.105, "selling_price": 0})  # price manager for the local electrical grid
        price_managing_heat_DLC = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_heat_DLC", {"nature": LTH.name, "buying_price": 0.95, "selling_price": 0})  # price manager for the local electrical grid

        price_managing_heat_flexible_producer = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_heat_flexible_producer", {"nature": LTH.name, "buying_price": 0, "selling_price": 0.1})  # price manager for the local electrical grid

    price_managing_elec_BAU = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_elec_BAU", {"nature": LVE.name, "buying_price": 0.17, "selling_price": 0.14})  # price manager for the local electrical grid
    price_managing_elec_DLC = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_elec_DLC", {"nature": LVE.name, "buying_price": 0.153, "selling_price": 0})  # price manager for the local electrical grid

    price_managing_elec_flexible_producer = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_elec_flexible_producer", {"nature": LVE.name, "buying_price": 0.17, "selling_price": 0.14})  # price manager for the local electrical grid

    price_managing_grid = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_elec_grid", {"nature": LVE.name, "buying_price": 0.17, "selling_price": 0.11})  # price manager for the local electrical grid

    subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 0.18, "limit_selling_price": -0.09})  # sets prices for the system operator
    subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0.306, "limit_selling_price": -0.153})  # sets prices for the system operator

    # Indoor temperature
    # this daemon is responsible for the value of indoor temperatures in the catalog
    indoor_temperature_daemon = subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

    # Outdoor temperature
    # this daemon is responsible for the value of outside temperature in the catalog
    outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Zaragoza"})

    # Water temperature
    # this daemon is responsible for the value of the water temperature in the catalog
    cold_water_temperature_daemon = subclasses_dictionary["Daemon"]["ColdWaterTemperatureDaemon"]({"location": "France"})

    # Irradiation
    # this daemon is responsible for updating the value of raw solar irradiation
    irradiation_daemon = subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Pau"})

    # Wind
    # this daemon is responsible for updating the value of raw solar Wind
    wind_daemon = subclasses_dictionary["Daemon"]["WindSpeedDaemon"]({"location": "Pau"})

    # Water flow
    # this daemon is responsible for updating the value of the flow of water for an electric dam
    water_flow_daemon = subclasses_dictionary["Daemon"]["WaterFlowDaemon"]({"location": "GavedePau_Pau"})

    # ##############################################################################################
    # Strategies

    # the local electrical grid strategy
    if strategy_exchange == "autarky":
        if strategy_distribution == "full":
            supervisor_elec = subclasses_dictionary["Strategy"][f"LightAutarkyEmergency"]()
            if grid == "mixed":  # if there is a DHN
                # the DHN strategy
                supervisor_heat = subclasses_dictionary["Strategy"][f"SubaggregatorHeatEmergency"]()

        elif strategy_distribution == "partial":
            supervisor_elec = subclasses_dictionary["Strategy"][f"LightAutarkyPartial"]()
            if grid == "mixed":  # if there is a DHN
                # the DHN strategy
                supervisor_heat = subclasses_dictionary["Strategy"][f"SubaggregatorHeatPartial"]()

    elif strategy_exchange == "profitable":
        if strategy_distribution == "full":
            supervisor_elec = subclasses_dictionary["Strategy"][f"WhenProfitableRevenues"]()
            if grid == "mixed":  # if there is a DHN
                # the DHN strategy
                    supervisor_heat = supervisor_elec

        elif strategy_distribution == "partial":
            supervisor_elec = subclasses_dictionary["Strategy"][f"WhenProfitablePartial"]()
            if grid == "mixed":  # if there is a DHN
                # the DHN strategy
                supervisor_heat = supervisor_elec

    elif strategy_exchange == "BAU":
        supervisor_elec = subclasses_dictionary["Strategy"][f"AlwaysSatisfied"]()
        if grid == "mixed":  # if there is a DHN
            # the DHN strategy
            supervisor_heat = subclasses_dictionary["Strategy"][f"SubaggregatorHeatEmergency"]()

    # the national grid strategy
    grid_supervisor = subclasses_dictionary["Strategy"]["Grid"]()

    # ##############################################################################################
    # Agents

    producer = Agent("producer")  # the owner of the energy plants

    national_grid = Agent("national_grid")

    local_electrical_grid_manager = Agent("local_electrical_grid_producer")  # the owner of the Photovoltaics panels

    DHN_manager = Agent("DHN_producer")  # the owner of the district heating network

    # ##############################################################################################
    # Contracts

    # contracts for aggregators
    contract_grid = subclasses_dictionary["Contract"]["EgoistContract"]("elec_grid_contract", LVE, price_managing_grid)

    # contracts for the production units
    if grid == "mixed":
        contract_DHN = subclasses_dictionary["Contract"]["CooperativeContract"]("DHN_contract", LVE, price_managing_elec_DLC)
        contract_flexible_production_heat = subclasses_dictionary["Contract"]["CooperativeContract"]("contract_flexible_production_heat", LTH, price_managing_heat_flexible_producer)

    contract_not_flexible_production_elec = subclasses_dictionary["Contract"]["EgoistContract"]("contract_production_elec", LVE, price_managing_elec_BAU)
    contract_flexible_production_elec = subclasses_dictionary["Contract"]["CooperativeContract"]("contract_flexible_production_elec", LVE, price_managing_elec_flexible_producer)

    # ##############################################################################################
    # Aggregators
    # national electrical grid
    aggregator_name = "elec_grid"
    aggregator_grid = Aggregator(aggregator_name, LVE, grid_supervisor, national_grid)

    # local electrical aggregator
    aggregator_name = "elec_aggregator"
    aggregator_elec = Aggregator(aggregator_name, LVE, supervisor_elec, local_electrical_grid_manager, aggregator_grid, contract_grid)  # creation of a aggregator

    # DHN aggregator
    if grid == "mixed":
        aggregator_name = "DHN_aggregator"
        if strategy_exchange != "BAU": # in cases with DSM, the power of the HP is considered "infinite" and equal to 10 MW otherwise
            aggregator_heat = Aggregator(aggregator_name, LTH, supervisor_heat, DHN_manager, aggregator_elec, contract_DHN, 2.5, {"buying": 7000, "selling": 0})  # creation of a aggregator
        else:
            aggregator_heat = Aggregator(aggregator_name, LTH, supervisor_heat, DHN_manager, aggregator_elec, contract_DHN, 2.5, {"buying": inf, "selling": 0})  # creation of a aggregator

    # ##############################################################################################
    # Devices

    # Production
    subclasses_dictionary["Device"]["PhotovoltaicsAdvanced"]("PV_field", contract_not_flexible_production_elec, producer, aggregator_elec, {"device": "standard_field"}, {"panels": 12500, "outdoor_temperature_daemon": outdoor_temperature_daemon.name, "irradiation_daemon": irradiation_daemon.name})  # creation of a photovoltaic panel field
    subclasses_dictionary["Device"]["WindTurbine"]("wind_turbine_1", contract_not_flexible_production_elec, producer, aggregator_elec, {"device": "ECOS_high"}, {"wind_speed_daemon": wind_daemon.name})  # creation of a wind turbine
    subclasses_dictionary["Device"]["WindTurbine"]("wind_turbine_2", contract_not_flexible_production_elec, producer, aggregator_elec, {"device": "ECOS_high"}, {"wind_speed_daemon": wind_daemon.name})  # creation of a wind turbine
    subclasses_dictionary["Device"]["WindTurbine"]("wind_turbine_3", contract_not_flexible_production_elec, producer, aggregator_elec, {"device": "ECOS_high"}, {"wind_speed_daemon": wind_daemon.name})  # creation of a wind turbine
    subclasses_dictionary["Device"]["WindTurbine"]("wind_turbine_4", contract_not_flexible_production_elec, producer, aggregator_elec, {"device": "ECOS_high"}, {"wind_speed_daemon": wind_daemon.name})  # creation of a wind turbine
    subclasses_dictionary["Device"]["WindTurbine"]("wind_turbine_5", contract_not_flexible_production_elec, producer, aggregator_elec, {"device": "ECOS_high"}, {"wind_speed_daemon": wind_daemon.name})  # creation of a wind turbine
    if grid == "mixed":
        subclasses_dictionary["Device"]["DummyProducer"]("heat_production", contract_flexible_production_heat, producer, aggregator_heat, {"device": "heat"}, {"max_power": 2000})  # creation of a heat production unit
    elif grid == "elec":
        subclasses_dictionary["Device"]["ElectricDam"]("electric_dam", contract_flexible_production_elec, producer, aggregator_elec, {"device": "Pelton"}, {"height": 5, "max_power": 3000, "water_flow_daemon": water_flow_daemon.name})  # creation of an electric dam

    # repartition of contracts according to the chosen proportion
    if DSM_proportion == 80:
        BAU = 200
        DLC = 480
        curtailment = 320
    elif DSM_proportion == 60:
        BAU = 400
        DLC = 360
        curtailment = 240
    elif DSM_proportion == 40:
        BAU = 600
        DLC = 240
        curtailment = 160
    elif DSM_proportion == 20:
        BAU = 800
        DLC = 120
        curtailment = 80
    elif DSM_proportion == 0:
        BAU = 1000
        DLC = 0
        curtailment = 0

    if grid == "mixed":
        # BAU contracts
        world.agent_generation("1_mixed_BAU", BAU * 2, "cases/Studies/EtudeDeCas2021/AgentTemplates/Agent_mixed_1_BAU.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec_BAU, "LTH": price_managing_heat_BAU}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
        world.agent_generation("2_mixed_BAU", BAU * 2, "cases/Studies/EtudeDeCas2021/AgentTemplates/Agent_mixed_2_BAU.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec_BAU, "LTH": price_managing_heat_BAU}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
        world.agent_generation("5_mixed_BAU", BAU, "cases/Studies/EtudeDeCas2021/AgentTemplates/Agent_mixed_5_BAU.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec_BAU, "LTH": price_managing_heat_BAU}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})

        # DLC contracts
        world.agent_generation("1_mixed_DLC", DLC * 2, "cases/Studies/EtudeDeCas2021/AgentTemplates/Agent_mixed_1_DLC.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec_DLC, "LTH": price_managing_heat_DLC}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
        world.agent_generation("2_mixed_DLC", DLC * 2, "cases/Studies/EtudeDeCas2021/AgentTemplates/Agent_mixed_2_DLC.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec_DLC, "LTH": price_managing_heat_DLC}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
        world.agent_generation("5_mixed_DLC", DLC, "cases/Studies/EtudeDeCas2021/AgentTemplates/Agent_mixed_5_DLC.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec_BAU, "LTH": price_managing_heat_BAU}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})

        # Curtailment contracts
        world.agent_generation("1_mixed_curtailment", curtailment * 2, "cases/Studies/EtudeDeCas2021/AgentTemplates/Agent_mixed_1_curtailment.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec_DLC, "LTH": price_managing_heat_DLC}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
        world.agent_generation("2_mixed_curtailment", curtailment * 2, "cases/Studies/EtudeDeCas2021/AgentTemplates/Agent_mixed_2_curtailment.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec_DLC, "LTH": price_managing_heat_DLC}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
        world.agent_generation("5_mixed_curtailment", curtailment, "cases/Studies/EtudeDeCas2021/AgentTemplates/Agent_mixed_5_curtailment.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec_BAU, "LTH": price_managing_heat_BAU}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})

    elif grid == "elec":
        # BAU contracts
        world.agent_generation("1_elec_BAU", BAU * 2, "cases/Studies/EtudeDeCas2021/AgentTemplates/Agent_elec_1_BAU.json", aggregator_elec, {"LVE": price_managing_elec_BAU}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
        world.agent_generation("2_elec_BAU", BAU * 2, "cases/Studies/EtudeDeCas2021/AgentTemplates/Agent_elec_2_BAU.json", aggregator_elec, {"LVE": price_managing_elec_BAU}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
        world.agent_generation("5_elec_BAU", BAU, "cases/Studies/EtudeDeCas2021/AgentTemplates/Agent_elec_5_BAU.json", aggregator_elec, {"LVE": price_managing_elec_BAU}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})

        # DLC contracts
        world.agent_generation("1_elec_DLC", DLC * 2, "cases/Studies/EtudeDeCas2021/AgentTemplates/Agent_elec_1_DLC.json", aggregator_elec, {"LVE": price_managing_elec_DLC}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
        world.agent_generation("2_elec_DLC", DLC * 2, "cases/Studies/EtudeDeCas2021/AgentTemplates/Agent_elec_2_DLC.json", aggregator_elec, {"LVE": price_managing_elec_DLC}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
        world.agent_generation("5_elec_DLC", DLC, "cases/Studies/EtudeDeCas2021/AgentTemplates/Agent_elec_5_DLC.json", aggregator_elec, {"LVE": price_managing_elec_DLC}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})

        # Curtailment contracts
        world.agent_generation("1_elec_curtailment", curtailment * 2, "cases/Studies/EtudeDeCas2021/AgentTemplates/Agent_elec_1_curtailment.json", aggregator_elec, {"LVE": price_managing_elec_DLC}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
        world.agent_generation("2_elec_curtailment", curtailment * 2, "cases/Studies/EtudeDeCas2021/AgentTemplates/Agent_elec_2_curtailment.json", aggregator_elec, {"LVE": price_managing_elec_DLC}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
        world.agent_generation("5_elec_curtailment", curtailment, "cases/Studies/EtudeDeCas2021/AgentTemplates/Agent_elec_5_curtailment.json", aggregator_elec, {"LVE": price_managing_elec_DLC}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})

    # ##############################################################################################
    # Dataloggers
    # datalogger for balances
    # these dataloggers record the balances for each agent, contract, nature and  cluster
    subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"](period="global")
    subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"](period=1)
    subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"](period="global")
    subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"](period=1)
    subclasses_dictionary["Datalogger"]["MismatchDatalogger"](period="global")

    subclasses_dictionary["Datalogger"]["WeightedSelfSufficiencyDatalogger"](period="global")
    subclasses_dictionary["Datalogger"]["SelfSufficiencyDatalogger"]()

    subclasses_dictionary["Datalogger"]["WeightedCurtailmentDatalogger"](period="global")
    subclasses_dictionary["Datalogger"]["CurtailmentDatalogger"]()

    # producers data, at each time step
    producer_datalogger = Datalogger("producer_datalogger", "ProdComplete")
    producer_datalogger.add("PV_field.LVE.energy_sold")
    producer_datalogger.add("PV_field.LVE.energy_erased")
    producer_datalogger.add("PV_field.LVE.money_earned")

    producer_datalogger.add("wind_turbine_1.LVE.energy_sold")
    producer_datalogger.add("wind_turbine_1.LVE.energy_erased")
    producer_datalogger.add("wind_turbine_1.LVE.money_earned")
    if grid == "mixed":
        producer_datalogger.add("heat_production.LTH.energy_sold")
        producer_datalogger.add("heat_production.LTH.energy_erased")
        producer_datalogger.add("heat_production.LTH.money_earned")
    elif grid == "elec":
        producer_datalogger.add("electric_dam.LVE.energy_sold")
        producer_datalogger.add("electric_dam.LVE.energy_erased")
        producer_datalogger.add("electric_dam.LVE.money_earned")

    producer_datalogger.add("producer.LVE.energy_sold")
    producer_datalogger.add("producer.LVE.energy_erased")
    producer_datalogger.add("producer.money_earned")

    # producers data, global data
    producer_datalogger = Datalogger("producer_datalogger_global", "ProdGlobal", "global")
    producer_datalogger.add("PV_field.LVE.energy_sold")
    producer_datalogger.add("PV_field.LVE.energy_erased")
    producer_datalogger.add("PV_field.LVE.money_earned")

    producer_datalogger.add("wind_turbine_1.LVE.energy_sold")
    producer_datalogger.add("wind_turbine_1.LVE.energy_erased")
    producer_datalogger.add("wind_turbine_1.LVE.money_earned")
    if grid == "mixed":
        producer_datalogger.add("heat_production.LTH.energy_sold")
        producer_datalogger.add("heat_production.LTH.energy_erased")
        producer_datalogger.add("heat_production.LTH.money_earned")
    elif grid == "elec":
        producer_datalogger.add("electric_dam.LVE.energy_sold")
        producer_datalogger.add("electric_dam.LVE.energy_erased")
        producer_datalogger.add("electric_dam.LVE.money_earned")

    producer_datalogger.add("producer.LVE.energy_sold")
    producer_datalogger.add("producer.LVE.energy_erased")
    producer_datalogger.add("producer.money_earned")

    # ##############################################################################################
    # Simulation
    # ##############################################################################################
    world.start()


