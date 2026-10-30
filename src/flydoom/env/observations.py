"""Learned and fly-inspired approximations for visual observation encoding.

These features are engineering approximations, not models of retinal physiology.
In particular, frame differences, Sobel responses, and expansion proxies do not
represent identified Drosophila cell types or their complete dynamics.
"""

from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F


def _images(observation: torch.Tensor) -> torch.Tensor:
    image = observation.float()
    if image.ndim == 3:
        image = image.unsqueeze(0)
    if image.shape[-1] in (1, 3):
        image = image.permute(0, 3, 1, 2)
    return image / 255.0 if image.max() > 1 else image


class SimpleCNNEncoder(nn.Module):
    """Small conventional CNN baseline producing a fixed visual latent."""

    def __init__(self, output_dim: int = 64) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Conv2d(3, 16, 5, stride=2),
            nn.ReLU(),
            nn.Conv2d(16, 32, 3, stride=2),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 4)),
            nn.Flatten(),
            nn.Linear(32 * 4 * 4, output_dim),
            nn.Tanh(),
        )
        self.output_dim = output_dim

    def forward(self, observation: torch.Tensor) -> torch.Tensor:
        return self.network(_images(observation))


class FlyInspiredVisualEncoder(nn.Module):
    """Pool luminance, contrast, directional edges, change, and looming proxies."""

    output_dim = 7 * 4 * 4

    def forward(
        self, observation: torch.Tensor, previous_observation: torch.Tensor | None = None
    ) -> torch.Tensor:
        image = _images(observation)
        luminance = image.mean(dim=1, keepdim=True)
        local_mean = F.avg_pool2d(luminance, 5, stride=1, padding=2)
        contrast = (luminance - local_mean).abs()
        sobel_x = luminance.new_tensor([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]).view(1, 1, 3, 3)
        sobel_y = sobel_x.transpose(-1, -2)
        horizontal = F.conv2d(luminance, sobel_x, padding=1).abs()
        vertical = F.conv2d(luminance, sobel_y, padding=1).abs()
        if previous_observation is None:
            temporal = torch.zeros_like(luminance)
        else:
            previous_luminance = _images(previous_observation).mean(dim=1, keepdim=True)
            temporal = (luminance - previous_luminance).abs()
        motion_x = horizontal * temporal
        motion_y = vertical * temporal
        center = luminance[
            ...,
            luminance.shape[-2] // 4 : -luminance.shape[-2] // 4,
            luminance.shape[-1] // 4 : -luminance.shape[-1] // 4,
        ]
        looming = F.interpolate(
            center, size=luminance.shape[-2:], mode="bilinear", align_corners=False
        )
        looming = (looming - luminance).relu()
        edges = (horizontal.square() + vertical.square()).sqrt()
        features = torch.cat(
            (luminance, temporal, contrast, motion_x, motion_y, looming, edges), dim=1
        )
        return F.adaptive_avg_pool2d(features, (4, 4)).flatten(1)


class CompoundEyeEncoder(nn.Module):
    """Bilateral hex-grid sampler with luminance, ON, OFF and change channels.

    This remains an engineering approximation: it models compound-eye sampling
    geometry and elementary temporal channels, not identified photoreceptor or
    lamina-neuron membrane dynamics.
    """

    channels_per_ommatidium = 4

    def __init__(self, rows: int = 8, columns_per_eye: int = 6) -> None:
        super().__init__()
        if rows < 2 or columns_per_eye < 2:
            raise ValueError("compound eye requires at least a 2x2 grid per eye")
        samples = []
        for eye in (-1, 1):
            x_min, x_max = (-0.95, -0.03) if eye < 0 else (0.03, 0.95)
            for row in range(rows):
                offset = 0.5 / columns_per_eye if row % 2 else 0.0
                for column in range(columns_per_eye):
                    fraction = (column + 0.5 + offset) / columns_per_eye
                    x = x_min + (x_max - x_min) * min(fraction, 0.98)
                    y = -0.92 + 1.84 * (row + 0.5) / rows
                    samples.append((x, y))
        self.register_buffer("sampling_grid", torch.tensor(samples).view(1, 1, -1, 2))
        self.ommatidia_per_eye = rows * columns_per_eye
        self.output_dim = 2 * self.ommatidia_per_eye * self.channels_per_ommatidium

    def forward(
        self, observation: torch.Tensor, previous_observation: torch.Tensor | None = None
    ) -> torch.Tensor:
        image = _images(observation)
        luminance = image.mean(dim=1, keepdim=True)
        grid = self.sampling_grid.expand(len(image), -1, -1, -1)
        current = F.grid_sample(luminance, grid, mode="bilinear", align_corners=False)
        current = current.flatten(1)
        if previous_observation is None:
            previous = current
        else:
            previous_luminance = _images(previous_observation).mean(dim=1, keepdim=True)
            previous = F.grid_sample(
                previous_luminance, grid, mode="bilinear", align_corners=False
            ).flatten(1)
        delta = current - previous
        on = delta.relu()
        off = (-delta).relu()
        change = delta.abs()
        return torch.stack((current, on, off, change), dim=-1).flatten(1)
