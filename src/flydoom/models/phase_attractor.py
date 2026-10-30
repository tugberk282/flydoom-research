"""Small explicit eight-phase attractor used as a testable CX intervention."""

from __future__ import annotations

import torch
from torch import nn


class EightPhaseAttractor(nn.Module):
    """Ring bump with separate persistence and phase-gated turn input.

    This is an intervention layer, not a claim that the raw scalar network already
    implements these equations.
    """

    def __init__(self, phases: int = 8, persistence: float = 0.9,
                 turn_strength: float = 0.35) -> None:
        super().__init__()
        if phases < 4 or not 0.0 <= persistence < 1.0:
            raise ValueError("invalid attractor parameters")
        self.phases = phases
        self.persistence = persistence
        self.turn_strength = turn_strength

    def normalize(self, profile: torch.Tensor) -> torch.Tensor:
        profile = profile.relu()
        return profile / profile.sum(dim=-1, keepdim=True).clamp_min(1e-8)

    def forward(self, profile: torch.Tensor, turn: torch.Tensor | None = None) -> torch.Tensor:
        if profile.ndim != 2 or profile.shape[-1] != self.phases:
            raise ValueError(f"profile must have shape [batch, {self.phases}]")
        current = self.normalize(profile)
        if turn is None:
            shifted = current
        else:
            if turn.shape != (len(profile),):
                raise ValueError("turn must have one integer value per batch item")
            shifted_rows = []
            for row, offset in zip(current, turn.long().tolist()):
                shifted_rows.append(torch.roll(row, int(offset), dims=0))
            shifted = torch.stack(shifted_rows)
        if turn is None:
            mixed = self.persistence * current + (1.0 - self.persistence) * shifted
        else:
            mixed = (1.0 - self.turn_strength) * current + self.turn_strength * shifted
        # Mild local competition keeps a bump while allowing the phase gate to move it.
        mixed = (mixed - mixed.mean(dim=-1, keepdim=True)).relu()
        return self.normalize(mixed)
