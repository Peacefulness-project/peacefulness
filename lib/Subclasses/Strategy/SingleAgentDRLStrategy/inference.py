# In this file, the trained model are run for inference
# Imports
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecNormalize
from lib.Subclasses.Strategy.SingleAgentDRLStrategy.PeacefulnessEnv import PeacefulnessEnv, datetime
from lib.Subclasses.Strategy.SingleAgentDRLStrategy.Utilities import recapitulate_state, recapitulate_decision, export_my_state_file, export_my_decision_file, plot_my_results

# Environment Parameters
my_path = "cases/Studies/first_paper_MultiEnergy/multiEnergyCaseStudy.py"
world_name = "MEG_single_DRL"
start_time = datetime(2020, 9, 22, 0, 0, 0)
simulation_length = 5304
export_path = "cases/Studies/first_paper_MultiEnergy/Results/Mono_agent/Inference"
obs_size = 46
action_info = {"total_size": 8, "exchanges": 3, "interior": {"electric_microgrid": 2, "district_heating_network": 3}}
obj = {"conservation_penalty": 5, "aggregator_costs": 1, "social_cost": 1, "gas_cost": 1,
       "waste_cost": 1, "heatSink_cost": 1,
       "green_injection": 1}
normalizing_parameters = {
                          # "energy_minimum": -25000.0, "energy_maximum": 35000.0,
                          # "price_minimum": 0.0, "price_maximum": 0.57,
                          }
performance_metrics = [
    "electric_microgrid.money_spent_outside", "electric_microgrid.money_earned_outside",  # external economic balance
    "flexible_loads.LVE.energy_erased", "flexible_loads.LVE.money",  # social cost
    "combined_heat_power.LPG.money_spent", "combined_heat_power.LPG.energy_wanted", "combined_heat_power.LVE.energy_wanted", "electric_microgrid.LVE.energy_wanted",  # gas cost
    "Waste_to_heat.heat_dissipated", "Waste_to_heat.LTH.energy_sold", "Waste_to_heat.LTH.money",  # cost of the wasted heat from the incinerator
    "combined_heat_power.heat_by_pass", "combined_heat_power.LTH.money",  # wasted heat from the CHP
    "PV_field_1.LVE.energy_sold", "PV_field_2.LVE.energy_sold", "WT_field_1.LVE.energy_sold", "WT_field_2.LVE.energy_sold",  # EnR
    "heat_pump.LVE.energy_bought", "heat_pump.LTH.energy_sold", "electric_microgrid.energy_bought_inside", "electric_microgrid.energy_bought_outside", "district_heating_network.energy_sold_inside"  # HP
]
act_red_dict = {
    "electric_microgrid": "Energy_Exchange_1",
    "district_heating_network": "Energy_Storage"
}

# Creating the environment for inference
MEG_caseStudy_env = make_vec_env(PeacefulnessEnv, n_envs=1, env_kwargs={"path_to_case": my_path, "world_name": world_name,
                                                     "start_time": start_time, "hours_to_simulate": simulation_length,
                                                     "export_path": export_path, "observation_size": obs_size,
                                                     "action_dict": action_info, "objective_dict": obj,
                                                     "normalization_dict": normalizing_parameters, "metrics": performance_metrics,
                                                     "red_dof_dict": act_red_dict, "std_dev": 0})

# Loading the trained model
# MEG_caseStudy_env = VecNormalize.load("cases/Studies/first_paper_MultiEnergy/Results/Mono_agent/Models/vecnormalize.pkl", MEG_caseStudy_env)
# MEG_caseStudy_env.training = False
# MEG_caseStudy_env.norm_reward = True
EMG_DHN_controller = PPO.load("cases/Studies/first_paper_MultiEnergy/Results/Mono_agent/Models/best_model/best_model.zip",
                              env=MEG_caseStudy_env)

# Global dicts for export
state_dict = {}
decision_dict = {}
max_nb_exchanges = 1
max_nb_conversions = 2

# Running inference
obs = MEG_caseStudy_env.reset()
done = [False]

while not done[0]:
    for k, v in recapitulate_state(MEG_caseStudy_env.envs[0].unwrapped.grid._catalog).items():
        for key, value in v.items():
            state_dict.setdefault(k, {}).setdefault(key, []).append(value)
    action, _states = EMG_DHN_controller.predict(
        obs,
        deterministic=True
    )
    obs, reward, done, info = MEG_caseStudy_env.step(action)
    if not done[0]:
        for k, v in recapitulate_decision(MEG_caseStudy_env.envs[0].unwrapped.grid._catalog).items():
            if "scope" not in k:  # we retrieve the decisions per aggregator
                decision_dict.setdefault(k, []).append(v)
    else:
        decision_dict["electric_microgrid.gym_Strategy.scaled_up_actions"].append(info[0]["electric_microgrid.gym_Strategy.scaled_up_actions"])
        decision_dict["district_heating_network.gym_Strategy.scaled_up_actions"].append(info[0]["district_heating_network.gym_Strategy.scaled_up_actions"])

export_my_state_file(state_dict, export_path + "_energy_intervals", max_nb_exchanges, max_nb_conversions)
export_my_decision_file(decision_dict, export_path + "_RL_decisions", max_nb_exchanges, max_nb_conversions)
plot_my_results(state_dict, decision_dict, export_path)

