# In this file, a dummy reward function is defined, it is useful in case of Potential Based Reward Shaping !
from typing import Dict, List

def define_my_Rt(*args):
    """
    *args : the necessary arguments to define the reward function we want to use
    """
    def dummyReward(iteration_result: Dict, metrics:List=None, agent_ID:str=None, action_reduction_dict:Dict=None):
        """
        iteration_result: the dataloggers' signal for each iteration used to compute the immediate reward
        """
        return 0.0

    return dummyReward
