# In this file, the trained agents are evaluated in the denoised environment

# Imports
from ray.rllib.algorithms.algorithm import Algorithm
from pprint import pprint

path_to_model = ""  # TODO à modifier à chaque RUN
loaded_model = Algorithm.from_checkpoint(path_to_model)
loaded_policy = loaded_model.get_policy()
loaded_policy.compute_single_action()

inference_results = loaded_model.evaluate()
pprint(inference_results)

