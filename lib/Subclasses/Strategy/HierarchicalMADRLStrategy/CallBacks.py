from ray.rllib.algorithms.callbacks import DefaultCallbacks


class EpisodicMetricsCallback(DefaultCallbacks):
    def __init__(self, agent_ID: str):
        super().__init__()
        self._agentID = agent_ID

    def on_episode_end(
        self,
        *,
        episode,
        prev_episode_chunks= None,
        env_runner= None,
        metrics_logger= None,
        env= None,
        env_index: int,
        rl_module= None,
        worker= None,
        base_env= None,
        policies= None,
        **kwargs,
    ):
        infos = episode.get_infos(agent_ids=self._agentID)
        # last element = last step's info for manager
        last_info = infos[self._agentID][-1] if infos else {}
        if last_info and "episode_metrics" in last_info:
            metrics = last_info['episode_metrics']

            metrics_logger.log_value("custom/sum_electricity_error", metrics["sum_error_EMG"])
            metrics_logger.log_value("custom/avg_electricity_error", metrics["avg_error_EMG"])
            metrics_logger.log_value("custom/max_electricity_error", metrics["max_error_EMG"])
            metrics_logger.log_value("custom/relative_electricity_error", metrics["relative_electricity_error"])
            metrics_logger.log_value("custom/sum_heat_error", metrics["sum_error_DHN"])
            metrics_logger.log_value("custom/avg_heat_error", metrics["avg_error_DHN"])
            metrics_logger.log_value("custom/max_heat_error", metrics["max_error_DHN"])
            metrics_logger.log_value("custom/relative_heat_error", metrics["relative_heat_error"])
            metrics_logger.log_value("custom/operational_costs", metrics["OPEX"])
            metrics_logger.log_value("custom/total_green_heat_supplied", metrics["total_green_supply"])
            metrics_logger.log_value("custom/external_balance", metrics["exchange_cost"])
            metrics_logger.log_value("custom/unsatisfied_flexible_loads", metrics["social_cost"])
            metrics_logger.log_value("custom/CHP_gas_costs", metrics["gas_cost"])
            metrics_logger.log_value("custom/CHP_unused_heat", metrics["CHP_heat_by_pass"])
            metrics_logger.log_value("custom/incinerator_heat_supply", metrics["incinerator_heat"])
            metrics_logger.log_value("custom/incinerator_unused_heat", metrics["W2h_dissipated_heat"])


def make_episodic_metrics_callback(agent_id: str):
    class _Wrapped(EpisodicMetricsCallback):
        def __init__(self):
            super().__init__(agent_ID=agent_id)
    return _Wrapped

