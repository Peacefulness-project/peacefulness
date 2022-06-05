from cases.Studies.ML. Script import run_simulation
import pandas as pd
import datetime
import gym  # RL library, https://www.gymlibrary.ml/

situations_to_test = pd.read_csv("")
situations_temporal_depth = 1  # manually set to test different results

# for line in situations_to_test:
#     start_date = line["start_date"]
#     run_simulation(start_date, situations_temporal_depth)
