# In this file the feasibility policy neural network's architecture is defined.
# The training loop according to Theile, et al. 2024 is also defined.

# Imports
import torch.nn as nn
from typing import Callable
from AmUtilities import *
from torch.utils.tensorboard import SummaryWriter


class FeasibilityPolicy(nn.Module):
    """
    The action mapper π_f(s_f, z) → a.
    Inputs are both normalized to [-1, 1].
    Output is tanh-squashed to [-1, 1].
    """
    def __init__(self, state_dim: int, latent_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim + latent_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, latent_dim),  # ensuring the output matches the action dimension
            nn.Tanh()  # ensuring output is bounded by [-1, 1]
        )

    def forward(self, relevant_s: torch.Tensor, latent_z: torch.Tensor) -> torch.Tensor:
        x = torch.cat([relevant_s, latent_z], dim=-1)
        return self.net(x)


class FeasibilityPolicyTrainer:
    """
    Here we define the training of the feasibility policy network.
    """
    def __init__(self, pi_f: FeasibilityPolicy, state_sampler: Callable, oracle: Callable, at_dim: int, latent_samples_per_state: int, states_per_batch: int, sigma: float, sigma_p: float, lr: float, norm_param: Dict, offset_threshold: float, path_to_data: str, agent_to_train, tensorboard_path: str, device: str = "cpu", state_1_dim: int=None, action_1_dim: int=None, nb_converters: int=None):
        self.mapper = pi_f.to(device)
        self.feasibility_model = oracle
        self.state_1_dim = state_1_dim
        self.at_1_dim = action_1_dim
        self.nb_converters = nb_converters
        self.state_sampler = state_sampler
        self.action_dim = at_dim
        self.K = states_per_batch
        self.N = latent_samples_per_state
        self.sigma = sigma
        self.sigma_prime = sigma_p
        self.optimizer = torch.optim.Adam(self.mapper.parameters(), lr)
        self.device = device
        self.norm_param = norm_param
        self.threshold = offset_threshold
        self.data = load_states(path_to_data, agent_to_train)
        self.writer = SummaryWriter(log_dir=tensorboard_path)  # Initializing the TensorBoard writer
        self.global_step = 0

    def training_step(self):
        """
        The inside loop of feasibility policy training from Algorithm 2 in Theile, et al. 2024.
        """
        self.optimizer.zero_grad()  # zeroing out the gradients before the loop
        total_loss = 0.0
        total_Z_hat = 0.0
        total_feasible = 0.0
        total_logq_mean = 0.0
        total_iw_mean = 0.0
        total_js_mean = 0.0
        for _ in range(min(self.K, len(self.data))):
            # 1.- Sampling one partial state
            s_f = self.state_sampler(self.data, self.norm_param)  # numpy array of obs_dim
            s_np = torch.tensor(s_f, dtype=torch.float32, device=self.device)  # transforming numpy array to a tensor
            s_batch = s_np.unsqueeze(0).expand(self.N, -1)  # adding a dim to the tensor (shape [N, obs_dim])

            # 2.- Sampling uniformly N latent vectors
            z_torch = torch.empty(self.N, self.action_dim, device=self.device).uniform_(-1.0, 1.0)

            # 3.- Mapping latent vectors to actions
            a_t = self.mapper(s_batch, z_torch)  # tensor of shape [N, act_dim]

            # 4.- Adding noise to get proposal samples
            eps = torch.randn_like(a_t) * self.sigma_prime
            a_star = (a_t + eps).detach()  # we detach so that torch doesn't "cheat" the learning

            # 5.- Estimation of the current probability distribution of the feasibility policy using KDE
            q_hat = kde(a_star, a_t, self.sigma, self.action_dim)  # tensor of shape [N]
            log_q = torch.log(q_hat + 1e-5)
            total_logq_mean += log_q.mean().item()  # for logging purposes
            q_hat_prime = kde(a_star, a_t.detach(), self.sigma_prime, self.action_dim)  # tensor of shape [N] - proposal distribution

            # 6.- Evaluation of the feasibility model
            with torch.no_grad():
                rj = self.feasibility_model(s_f, a_star.cpu().numpy(), self.norm_param, self.threshold, self.state_1_dim, self.at_1_dim, self.nb_converters)
                rj = torch.tensor(rj, dtype=torch.float32, device=self.device)
                total_feasible += rj.mean().item()  # for logging purposes

                # 7.- Estimation of the partition function using Monte-Carlo and Importance Sampling
                z_hat = (rj / (q_hat_prime + 1e-5)).mean()  # scalar
                total_Z_hat += z_hat.item()  # for logging purposes

                # 8.- Estimation of the target probability distribution
                p_hat = rj / (z_hat + 1e-5)  # tensor of shape [N]

                # 9.- Computing the divergence between the current nad target probability distributions using JS loss
                iw = q_hat / (q_hat_prime + 1e-5)  # importance sampling
                total_iw_mean += iw.mean().item()  # for logging purposes
                js_score = torch.log(2 * q_hat / (q_hat + p_hat + 1e-5) + 1e-5)
                total_js_mean += js_score.mean().item()  # for logging purposes
            loss = (iw.detach() * js_score.detach() * log_q).mean() / (2.0 * self.K)

            # 10.- Backpropagation ; computing and accumulating gradients
            loss.backward()
            total_loss += loss.item()  # for logging the loss over training iterations

        # 11.- Applying gradients to feasibility policy weights
        self.optimizer.step()

        # Logging metrics to Tensorboard for each training iteration
        self.writer.add_scalar("train/loss", total_loss, self.global_step)
        self.writer.add_scalar("train/Z_hat", total_Z_hat / self.K, self.global_step)
        self.writer.add_scalar("train/feasible_ratio", total_feasible / self.K, self.global_step)
        self.writer.add_scalar("train/importance_weight", total_iw_mean / self.K, self.global_step)
        self.writer.add_scalar("train/log_q_distribution", total_logq_mean / self.K, self.global_step)
        self.writer.add_scalar("train/js_score", total_js_mean / self.K, self.global_step)
        total_norm = nn.utils.clip_grad_norm_(self.mapper.parameters(), max_norm=0.5)
        self.writer.add_scalar("train/grad_norm", total_norm, self.global_step)
        self.global_step += 1

    def train(self, num_steps: int, eval_interval: int):
        """
        The outer loop of feasibility policy training from Algorithm 2 in Theile, et al. 2024.
        """
        for step in range(num_steps):
            # Training step
            self.training_step()

            # Evaluation step - performing a feasibility test with true actions
            if step % eval_interval == 0:
                with torch.no_grad():
                    # sampling a state from the data
                    s_t = self.state_sampler(self.data, self.norm_param)
                    sn_f = torch.tensor(s_t, dtype=torch.float32, device=self.device)
                    s_batch = sn_f.unsqueeze(0).expand(self.N, -1)
                    # uniform sampling latents
                    z = torch.empty(self.N, self.action_dim, device=self.device).uniform_(-1.0, 1.0)
                    # outputting pure actions from the action mapper model
                    pure_actions = self.mapper(s_batch, z)
                    # checking the constraint satisfaction
                    validity_array = self.feasibility_model(s_t, pure_actions.cpu().numpy(), self.norm_param, self.threshold, self.state_1_dim, self.at_1_dim, self.nb_converters)
                    true_feasible_ratio = validity_array.mean()
                # Log the True Feasibility to TensorBoard
                self.writer.add_scalar("eval/true_feasible_ratio", true_feasible_ratio, step)

        self.writer.close()  # Closing the TensorBoard writer when training is completed

    def save(self, path_to_save: str):
        """
        This method is used to save the trained model.
        """
        torch.save(self.mapper.state_dict(), path_to_save)
