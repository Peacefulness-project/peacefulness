from cases.Studies.ML. SimulationScript import create_simulation
# import gym  # RL library, https://www.gymlibrary.ml/
from cases.Studies.ML.Clustering import clustering
from cases.Studies.ML.Training import training
from cases.Studies.ML.Comparison import comparison

# situations_to_test = pd.read_csv("")
# situations_temporal_depth = 1  # manually set to test different results

# for line in situations_to_test:
#     start_date = line["start_date"]
#     create_simulation(start_date, situations_temporal_depth)

# parameters
simulation_length = 24


# clustering
clustering(simulation_length)


# training
training()


# comparison
comparison()



