"""Population-vector measurements for PB glomerular activity."""

from __future__ import annotations

import re

import numpy as np


PB_GLOMERULUS = re.compile(r"_([LR])(\d+)(?:_|$)")
EPG_ORDER = tuple([f"L{i}" for i in range(1, 9)] + [f"R{i}" for i in range(8, 0, -1)])
PEN_ORDER = tuple([f"L{i}" for i in range(2, 10)] + [f"R{i}" for i in range(9, 1, -1)])


def pb_label(instance: str) -> str | None:
    """Extract a PB glomerulus such as L3 from an official instance label."""
    match = PB_GLOMERULUS.search(str(instance))
    return None if match is None else f"{match.group(1)}{int(match.group(2))}"


def phase_bins(instances, order=EPG_ORDER) -> np.ndarray:
    """Map instance labels to circular PB-bin indices; unknown labels become -1."""
    positions = {label: index for index, label in enumerate(order)}
    return np.asarray([positions.get(pb_label(value), -1) for value in instances], dtype=np.int64)


def epg_functional_bins(instances) -> np.ndarray:
    """Map bilateral PB EPG columns onto eight connectivity-supported compass phases."""
    anatomical = phase_bins(instances, EPG_ORDER)
    return np.where(anatomical < 0, -1, anatomical % 8)


def pen_functional_bins(instances) -> np.ndarray:
    """Map bilateral PEN PB columns onto eight functional compass phases."""
    anatomical = phase_bins(instances, PEN_ORDER)
    return np.where(anatomical < 0, -1, anatomical % 8)


def population_vector(activity: np.ndarray, bins: np.ndarray, bin_count: int | None = None):
    """Return phase, concentration and binned activity for each sample."""
    values = np.asarray(activity, dtype=np.float64)
    if values.ndim == 1:
        values = values[None, :]
    if values.shape[1] != len(bins):
        raise ValueError("activity columns and phase bins must have equal length")
    if bin_count is None:
        valid = bins[bins >= 0]
        if not len(valid):
            raise ValueError("at least one valid phase bin is required")
        bin_count = int(valid.max()) + 1
    binned = np.zeros((len(values), bin_count), dtype=np.float64)
    for index in range(bin_count):
        selected = bins == index
        if np.any(selected):
            binned[:, index] = values[:, selected].mean(axis=1)
    # Neural states can be signed. A bump is defined relative to the least active bin.
    nonnegative = binned - binned.min(axis=1, keepdims=True)
    angles = np.arange(bin_count) * (2 * np.pi / bin_count)
    vector = (nonnegative * np.exp(1j * angles)).sum(axis=1)
    mass = nonnegative.sum(axis=1)
    concentration = np.divide(np.abs(vector), mass, out=np.zeros_like(mass), where=mass > 0)
    return np.angle(vector), concentration, binned


def heading_phase_coherence(phase: np.ndarray, heading: np.ndarray) -> float:
    """Rotation/offset-invariant coupling between phase and four maze headings."""
    heading_angle = np.asarray(heading) * (np.pi / 2)
    return float(np.abs(np.mean(np.exp(1j * (np.asarray(phase) - heading_angle)))))
