from cases.Studies.ML. SimulationScript import create_simulation
import pandas as pd
from random import shuffle
import datetime


def dummy_order_priorities_conso(strategy: "Strategy"):
    ordered_list = ["store", "soft_DSM_conso", "hard_DSM_conso", "buy_outside_emergency"]
    shuffle(ordered_list)
    return ordered_list


def dummy_order_priorities_prod(strategy: "Strategy"):
    ordered_list = ["soft_DSM_prod", "hard_DSM_prod", "sell_outside_emergency", "unstore"]
    shuffle(ordered_list)
    return ordered_list


def clustering(simulation_length):
    start_date = datetime.datetime(year=2018, month=1, day=1, hour=1,)
    location = "Santerre"  # location used for meteo daemons
    parameters = [  # prices are not taken into account for now
        # meteo

        # storage
        "battery.energy_stored",
        # consumption
        "LVE.minimum_energy_consumption",
        "LVE.maximum_energy_consumption",
    ]

    # + demand en attente

    situations = pd.DataFrame(columns=parameters)
    for i in range(1):
        start_date += datetime.timedelta(hours=1)
        catalog = create_simulation(start_date, simulation_length, dummy_order_priorities_conso,
                                    dummy_order_priorities_prod, location)
        buffer_dict = {}





