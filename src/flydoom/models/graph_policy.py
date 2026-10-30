"""Actor-critic policy constrained to sensory inputs and descending readouts."""

from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F
from torch.distributions import Categorical

from flydoom.env.observations import CompoundEyeEncoder, FlyInspiredVisualEncoder, SimpleCNNEncoder
from flydoom.models.connectome_network import ConnectomeRateNetwork
from flydoom.models.phase_attractor import EightPhaseAttractor


class ConnectomePolicy(nn.Module):
    """Encode pixels into sensory nodes and read actions/value from descending nodes."""

    def __init__(
        self,
        network: ConnectomeRateNetwork,
        sensory_indices: torch.Tensor,
        descending_indices: torch.Tensor,
        action_count: int = 5,
        encoder: str = "cnn",
        propagation_steps: int = 5,
        training_mode: str = "trainable_internal",
        sensory_side_codes: torch.Tensor | None = None,
        output_side_codes: torch.Tensor | None = None,
        default_forward_steering: bool = False,
        efference_indices: torch.Tensor | None = None,
        efference_action_mask: torch.Tensor | None = None,
        fixed_positive_efference: bool = False,
        efference_gain: float = 0.3,
        efference_phase_source_indices: torch.Tensor | None = None,
        efference_source_bins: torch.Tensor | None = None,
        efference_target_bins: torch.Tensor | None = None,
        phase_core_epg_indices: torch.Tensor | None = None,
        phase_core_epg_bins: torch.Tensor | None = None,
        explicit_phase_core: bool = False,
        phase_prior: bool = False,
        phase_prior_gain: float = 0.3,
        phase_required: bool = False,
    ) -> None:
        super().__init__()
        if not len(sensory_indices) or not len(descending_indices):
            raise ValueError("Policy requires sensory and descending neuron populations")
        self.network = network
        self.register_buffer("sensory_indices", sensory_indices.long())
        self.register_buffer("descending_indices", descending_indices.long())
        if encoder not in {"cnn", "fly", "compound_eye"}:
            raise ValueError("encoder must be 'cnn', 'fly' or 'compound_eye'")
        encoders = {
            "cnn": lambda: SimpleCNNEncoder(64),
            "fly": FlyInspiredVisualEncoder,
            "compound_eye": CompoundEyeEncoder,
        }
        self.encoder = encoders[encoder]()
        self.input_mapping = nn.Linear(self.encoder.output_dim, len(sensory_indices))
        input_mask = torch.ones(len(sensory_indices), self.encoder.output_dim)
        resolved_side_codes = torch.zeros(len(sensory_indices), dtype=torch.int8)
        if sensory_side_codes is not None:
            if encoder != "compound_eye":
                raise ValueError("bilateral sensory mapping requires compound_eye encoder")
            if len(sensory_side_codes) != len(sensory_indices):
                raise ValueError("one sensory side code is required per sensory neuron")
            eye_features = self.encoder.output_dim // 2
            resolved_side_codes = sensory_side_codes.to(dtype=torch.int8, device="cpu")
            input_mask[sensory_side_codes < 0, eye_features:] = 0
            input_mask[sensory_side_codes > 0, :eye_features] = 0
        self.register_buffer("input_mask", input_mask)
        self.register_buffer("sensory_side_codes", resolved_side_codes)
        self.register_buffer("sensory_active_mask", torch.ones(len(sensory_indices)))
        self.action_readout = nn.Linear(len(descending_indices), action_count)
        action_mask = torch.ones(action_count, len(descending_indices))
        resolved_output_sides = torch.zeros(len(descending_indices), dtype=torch.int8)
        if output_side_codes is not None:
            if action_count != 3:
                raise ValueError("side-constrained motor readout currently requires 3 actions")
            if len(output_side_codes) != len(descending_indices):
                raise ValueError("one output side code is required per readout neuron")
            resolved_output_sides = output_side_codes.to(dtype=torch.int8, device="cpu")
            # Testable laterality hypothesis: ipsilateral population supports its turn;
            # bilateral motor activity supports forward locomotion.
            action_mask[0, output_side_codes >= 0] = 0
            action_mask[2, output_side_codes <= 0] = 0
            if default_forward_steering:
                # DNa02 supplies differential steering; forward locomotion is the
                # basal action represented by the learnable action bias.
                action_mask[1].zero_()
            # Equalize initial logit variance across actions with different
            # population sizes; otherwise bilateral forward has an unfair scale.
            fan_in = action_mask.sum(dim=1, keepdim=True)
            scale = torch.where(
                fan_in > 0, (len(descending_indices) / fan_in.clamp_min(1)).sqrt(),
                torch.ones_like(fan_in),
            )
            action_mask *= scale
        self.register_buffer("action_readout_mask", action_mask)
        self.register_buffer("output_side_codes", resolved_output_sides)
        self.register_buffer("output_active_mask", torch.ones(len(descending_indices)))
        resolved_efference = (
            torch.empty(0, dtype=torch.long)
            if efference_indices is None else efference_indices.long()
        )
        self.register_buffer("efference_indices", resolved_efference)
        self.efference_mapping = (
            nn.Linear(action_count, len(resolved_efference), bias=False)
            if len(resolved_efference) else None
        )
        if self.efference_mapping is not None and fixed_positive_efference:
            self.efference_mapping.weight.data.fill_(efference_gain)
            self.efference_mapping.weight.requires_grad_(False)
        resolved_efference_mask = torch.ones(len(resolved_efference), action_count)
        if efference_action_mask is not None:
            if efference_action_mask.shape != resolved_efference_mask.shape:
                raise ValueError(
                    "efference_action_mask must have shape [efference cells, actions]"
                )
            resolved_efference_mask = efference_action_mask.float()
        # Experimental topology metadata should not invalidate legacy checkpoints.
        self.register_buffer(
            "efference_action_mask", resolved_efference_mask, persistent=False
        )
        phase_sources = (torch.empty(0, dtype=torch.long)
                         if efference_phase_source_indices is None
                         else efference_phase_source_indices.long())
        source_bins = (torch.empty(0, dtype=torch.long) if efference_source_bins is None
                       else efference_source_bins.long())
        target_bins = (torch.empty(0, dtype=torch.long) if efference_target_bins is None
                       else efference_target_bins.long())
        if len(phase_sources) and (len(source_bins) != len(phase_sources)
                                   or len(target_bins) != len(resolved_efference)):
            raise ValueError("phase-gated efference requires one bin per source and target")
        self.register_buffer("efference_phase_source_indices", phase_sources, persistent=False)
        self.register_buffer("efference_source_bins", source_bins, persistent=False)
        self.register_buffer("efference_target_bins", target_bins, persistent=False)
        core_indices = (torch.empty(0, dtype=torch.long) if phase_core_epg_indices is None
                        else phase_core_epg_indices.long())
        core_bins = (torch.empty(0, dtype=torch.long) if phase_core_epg_bins is None
                     else phase_core_epg_bins.long())
        if explicit_phase_core and (len(core_indices) == 0 or len(core_bins) != len(core_indices)):
            raise ValueError("explicit phase core requires EPG indices and bins")
        self.register_buffer("phase_core_epg_indices", core_indices, persistent=False)
        self.register_buffer("phase_core_epg_bins", core_bins, persistent=False)
        self.phase_prior = bool(phase_prior)
        self.phase_prior_gain = float(phase_prior_gain)
        self.phase_required = bool(phase_required)
        self.phase_prior_readout = nn.Linear(8, action_count, bias=False) if self.phase_prior else None
        self.explicit_phase_core = explicit_phase_core
        self.phase_core = EightPhaseAttractor(persistence=0.9, turn_strength=1.0)
        self.value_readout = nn.Linear(len(descending_indices), 1)
        self.propagation_steps = propagation_steps
        self.training_mode = training_mode
        if training_mode not in {
            "trainable_internal",
            "fixed_internal",
            "readout_only",
            "three_factor",
        }:
            raise ValueError(f"Unknown training mode: {training_mode}")
        if training_mode in {"fixed_internal", "readout_only", "three_factor"}:
            self.network.edge_weight.requires_grad_(False)
            self.network.bias.requires_grad_(False)
        if training_mode == "readout_only":
            for module in (self.encoder, self.input_mapping):
                for parameter in module.parameters():
                    parameter.requires_grad_(False)
        if training_mode == "three_factor":
            for parameter in self.parameters():
                parameter.requires_grad_(False)

    def forward(self, observation: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        logits, value, _ = self.forward_with_activity(observation)
        return logits, value

    def forward_with_activity(
        self, observation: torch.Tensor, state: torch.Tensor | None = None,
        previous_action: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Return policy outputs plus the full node state for synchronized recording."""
        latent = self.encoder(observation)
        external = latent.new_zeros((latent.shape[0], self.network.node_count))
        sensory_drive = F.linear(
            latent, self.input_mapping.weight * self.input_mask, self.input_mapping.bias
        )
        external[:, self.sensory_indices] = (
            torch.tanh(sensory_drive) * self.sensory_active_mask
        )
        if not getattr(self, "suppress_efference", False) and self.efference_mapping is not None and previous_action is not None:
            efference_drive = torch.tanh(
                F.linear(
                    previous_action,
                    self.efference_mapping.weight * self.efference_action_mask,
                )
            )
            if len(self.efference_phase_source_indices) and state is not None:
                source_state = state[:, self.efference_phase_source_indices]
                phase_profile = torch.stack([
                    source_state[:, self.efference_source_bins == phase].mean(dim=1)
                    for phase in range(8)
                ], dim=1)
                phase_gate = torch.softmax(phase_profile * 8.0, dim=1) * 8.0
                efference_drive = efference_drive * phase_gate[
                    :, self.efference_target_bins
                ]
            external[:, self.efference_indices] += efference_drive
        if getattr(self, "suppress_pen_drive", False) and len(self.efference_indices):
            external[:, self.efference_indices] = 0
        next_state = self.network(external, state=state, steps=self.propagation_steps)
        if self.explicit_phase_core and len(self.phase_core_epg_indices):
            epg_state = next_state[:, self.phase_core_epg_indices]
            visual_profile = torch.stack([
                epg_state[:, self.phase_core_epg_bins == phase].mean(dim=1)
                for phase in range(8)
            ], dim=1)
            profile = visual_profile
            if state is not None:
                retained = state[:, self.phase_core_epg_indices]
                profile = torch.stack([
                    retained[:, self.phase_core_epg_bins == phase].mean(dim=1)
                    for phase in range(8)
                ], dim=1)
            turn = None
            if previous_action is not None and not getattr(self, "suppress_efference", False):
                turn = previous_action[:, 2] * 2 - previous_action[:, 0] * 2
            profile = self.phase_core(profile, turn)
            if state is not None:
                visual_profile = self.phase_core.normalize(visual_profile)
                profile = self.phase_core.normalize(0.85 * profile + 0.15 * visual_profile)
            next_state = next_state.clone()
            next_state[:, self.phase_core_epg_indices] = profile[:, self.phase_core_epg_bins]
        if getattr(self, "suppress_epg_state", False) and len(self.phase_core_epg_indices):
            next_state = next_state.clone()
            next_state[:, self.phase_core_epg_indices] = 0
        suppress_indices = getattr(self, "suppress_state_indices", None)
        if suppress_indices is not None and len(suppress_indices):
            next_state = next_state.clone()
            next_state[:, suppress_indices] = 0
        descending = (
            next_state[:, self.descending_indices] * self.output_active_mask
        )
        phase_bias = None
        phase_profile = None
        if self.phase_prior and len(self.phase_core_epg_indices):
            phase_state = next_state[:, self.phase_core_epg_indices]
            phase_profile = torch.stack([
                phase_state[:, self.phase_core_epg_bins == phase].mean(dim=1)
                for phase in range(8)
            ], dim=1)
            phase_bias = self.phase_prior_gain * self.phase_prior_readout(phase_profile)
            # The EPG prior is a steering prior, not a locomotion/forward drive.
            # Keep the forward logit exclusively under the motor-route branch.
            if phase_bias.shape[1] >= 3:
                phase_bias = phase_bias.clone()
                phase_bias[:, 1] = 0.0
        logits = F.linear(
                descending,
                self.action_readout.weight * self.action_readout_mask,
                self.action_readout.bias,
            )
        if self.phase_required and len(self.phase_core_epg_indices):
            if phase_profile is None:
                phase_state = next_state[:, self.phase_core_epg_indices]
                phase_profile = torch.stack([phase_state[:, self.phase_core_epg_bins == p].mean(dim=1) for p in range(8)], dim=1)
            confidence = phase_profile.abs().max(dim=1).values.clamp(0.05, 1.0)
            logits = logits.clone(); logits[:, 0] *= confidence; logits[:, 2] *= confidence
        return (
            logits + (phase_bias if phase_bias is not None else 0.0),
            self.value_readout(descending).squeeze(-1),
            next_state,
        )

    def initial_state(self, batch_size: int, device: torch.device):
        brain = torch.zeros(batch_size, self.network.node_count, device=device)
        if self.efference_mapping is None:
            return brain
        previous_action = torch.zeros(
            batch_size, self.action_readout.out_features, device=device
        )
        return brain, previous_action

    def forward_recurrent(
        self, observation: torch.Tensor, state
    ):
        if isinstance(state, tuple):
            brain, previous_action = state
            logits, value, next_brain = self.forward_with_activity(
                observation, brain, previous_action
            )
            return logits, value, (next_brain, previous_action)
        return self.forward_with_activity(observation, state)

    def set_sensory_ablation(self, side: str = "none") -> None:
        """Disable anatomically annotated sensory neurons on one soma/root side."""
        self.sensory_active_mask.fill_(1)
        code = -1 if side.upper() == "L" else 1 if side.upper() == "R" else 0
        if side.lower() != "none" and code == 0:
            raise ValueError("side must be 'none', 'L' or 'R'")
        if code:
            self.sensory_active_mask[self.sensory_side_codes == code] = 0

    def set_output_ablation(self, side: str = "none") -> None:
        """Disable readout neurons on one anatomically annotated side."""
        self.output_active_mask.fill_(1)
        code = -1 if side.upper() == "L" else 1 if side.upper() == "R" else 0
        if side.lower() != "none" and code == 0:
            raise ValueError("side must be 'none', 'L' or 'R'")
        if code:
            self.output_active_mask[self.output_side_codes == code] = 0

    def act(
        self, observation: torch.Tensor, deterministic: bool = False
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        logits, value = self(observation)
        distribution = Categorical(logits=logits)
        action = logits.argmax(dim=-1) if deterministic else distribution.sample()
        return action, distribution.log_prob(action), value

    def act_recurrent(
        self,
        observation: torch.Tensor,
        state: torch.Tensor,
        deterministic: bool = False,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        logits, value, next_state = self.forward_recurrent(observation, state)
        distribution = Categorical(logits=logits)
        action = logits.argmax(dim=-1) if deterministic else distribution.sample()
        if isinstance(next_state, tuple):
            next_state = (
                next_state[0],
                F.one_hot(action, self.action_readout.out_features).to(
                    dtype=next_state[0].dtype
                ),
            )
        return action, distribution.log_prob(action), value, next_state

    def evaluate_actions(
        self, observation: torch.Tensor, action: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        logits, value = self(observation)
        distribution = Categorical(logits=logits)
        return distribution.log_prob(action), distribution.entropy(), value

    def evaluate_actions_recurrent(
        self, observation: torch.Tensor, action: torch.Tensor, state: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        logits, value, _ = self.forward_recurrent(observation, state)
        distribution = Categorical(logits=logits)
        return distribution.log_prob(action), distribution.entropy(), value
