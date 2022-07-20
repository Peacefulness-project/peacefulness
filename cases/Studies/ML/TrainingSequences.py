from cases.Studies.ML. Script import run_simulation
import pandas as pd
import datetime
import gym  # RL library, https://www.gymlibrary.ml/

# situations_to_test = pd.read_csv("")
# situations_temporal_depth = 1  # manually set to test different results

# for line in situations_to_test:
#     start_date = line["start_date"]
#     run_simulation(start_date, situations_temporal_depth)

start_date = datetime.datetime(year=2018, month=1, day=1, hour=1,)
priorities_conso = ["store", "soft_DSM_conso", "hard_DSM_conso", "buy_outside_emergency"]
priorities_prod = ["soft_DSM_prod", "hard_DSM_prod", "sell_outside_emergency", "unstore"]
simulation_length = 24

run_simulation(start_date, simulation_length, priorities_conso, priorities_prod)
