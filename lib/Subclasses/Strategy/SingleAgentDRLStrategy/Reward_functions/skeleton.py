# In this file, the template of reward functions is showcased for future reward functions to be defined !
from typing import Dict, List

def define_my_Rt(*args):
    """
    *args : the necessary arguments to define the reward function we want to use
    """
    def my_Rt(iteration_result: Dict, metrics:List=None, agent_ID:str=None, action_reduction_dict:Dict=None):
        """
        iteration_result: the dataloggers' signal for each iteration used to compute the immediate reward
        """
        return 0.0

    return my_Rt
