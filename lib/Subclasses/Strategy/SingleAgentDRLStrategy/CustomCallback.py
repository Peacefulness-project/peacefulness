from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.vec_env import sync_envs_normalization


class EpisodicMetricsCallback(BaseCallback):

    def __init__(self, verbose=0):
        super().__init__(verbose)

    def _on_step(self) -> bool:

        infos = self.locals["infos"]
        dones = self.locals["dones"]
        for done, info in zip(dones, infos):
            if done:
                if "episode_metrics" in info:
                    metrics = info["episode_metrics"]

                    self.logger.record(
                        "custom/sum_electricity_error",
                        metrics["sum_error_EMG"]
                    )
                    self.logger.record(
                        "custom/avg_electricity_error",
                        metrics["avg_error_EMG"]
                    )
                    self.logger.record(
                        "custom/max_electricity_error",
                        metrics["max_error_EMG"]
                    )
                    self.logger.record(
                        "custom/relative_electricity_error",
                        metrics["relative_electricity_error"]
                    )
                    self.logger.record(
                        "custom/sum_heat_error",
                        metrics["sum_error_DHN"]
                    )
                    self.logger.record(
                        "custom/avg_heat_error",
                        metrics["avg_error_DHN"]
                    )
                    self.logger.record(
                        "custom/max_heat_error",
                        metrics["max_error_DHN"]
                    )
                    self.logger.record(
                        "custom/relative_heat_error",
                        metrics["relative_heat_error"]
                    )
                    self.logger.record(
                        "custom/operational_costs",
                        metrics["OPEX"]
                    )
                    self.logger.record(
                        "custom/total_green_heat_supplied",
                        metrics["total_green_supply"]
                    )
                    self.logger.record(
                        "custom/external_balance",
                        metrics["exchange_cost"]
                    )
                    self.logger.record(
                        "custom/unsatisfied_flexible_loads",
                        metrics["social_cost"]
                    )
                    self.logger.record(
                        "custom/unsatisfied_flexible_loads",
                        metrics["social_cost"]
                    )
                    self.logger.record(
                        "custom/CHP_gas_costs",
                        metrics["gas_cost"]
                    )
                    self.logger.record(
                        "custom/CHP_unused_heat",
                        metrics["CHP_heat_by_pass"]
                    )
                    self.logger.record(
                        "custom/Incinerator_heat_supply",
                        metrics["incinerator_heat"]
                    )
                    self.logger.record(
                        "custom/Incinerator_unused_heat",
                        metrics["W2h_dissipated_heat"]
                    )

        return True


class NormalizedEvalCallback(EvalCallback):

    def _on_step(self) -> bool:

        sync_envs_normalization(
            self.training_env,
            self.eval_env
        )

        return super()._on_step()