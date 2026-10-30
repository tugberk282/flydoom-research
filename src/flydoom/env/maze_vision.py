"""Deterministic first-person camera renderer for grid-maze experiments."""

from __future__ import annotations

import math

import numpy as np


PORTAL_COLOR = np.asarray((32, 240, 160), dtype=np.uint8)


def add_celestial_compass_cue(frame: np.ndarray, heading: int) -> np.ndarray:
    """Overlay a world-fixed panoramic sky cue for landmark-anchor experiments."""
    result = np.asarray(frame).copy()
    width = result.shape[1]
    band_height = max(3, result.shape[0] // 6)
    screen_angle = np.linspace(-np.pi / 2, np.pi / 2, width, endpoint=False)
    world_angle = screen_angle + heading * (np.pi / 2)
    signal = (0.5 + 0.5 * np.cos(world_angle)).astype(np.float32)
    quadrature = (0.5 + 0.5 * np.sin(world_angle)).astype(np.float32)
    result[:band_height, :, 2] = np.clip(40 + 200 * signal, 0, 255).astype(np.uint8)
    result[:band_height, :, 0] = np.clip(20 + 50 * (1 - signal), 0, 255).astype(np.uint8)
    result[:band_height, :, 1] = np.clip(30 + 180 * quadrature, 0, 255).astype(np.uint8)
    return result


def add_goal_vector_cue(frame: np.ndarray, dx: int, dy: int, heading: int) -> np.ndarray:
    """Encode egocentric exit direction in a narrow, non-visual control band.

    This makes the maze task identifiable across maze sizes while leaving the
    rendered scene unchanged below the band.  The cue is deliberately low
    bandwidth: horizontal position encodes bearing and intensity encodes
    normalized distance.
    """
    result = np.asarray(frame).copy()
    width = result.shape[1]
    band = max(2, result.shape[0] // 16)
    # rotate world vector into the agent's egocentric frame
    for _ in range(int(heading) % 4):
        dx, dy = dy, -dx
    bearing = float(np.arctan2(dy, dx))
    center = int(np.clip((bearing / np.pi + 0.5) * width, 0, width - 1))
    distance = min(1.0, float(np.hypot(dx, dy)) / 32.0)
    radius = max(1, width // 16)
    result[:band] = 0
    result[:band, max(0, center-radius):min(width, center+radius+1), 1] = int(80 + 175 * (1-distance))
    result[:band, max(0, center-radius):min(width, center+radius+1), 2] = int(220 * (1-distance))
    return result


def render_maze_camera(
    grid: list[str], x: int, y: int, heading: int, *, width: int = 64, height: int = 48,
    field_of_view: float = math.radians(110), max_distance: float = 12.0,
) -> np.ndarray:
    """Render an egocentric RGB view using one ray per image column."""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    horizon = height // 2
    frame[:horizon] = (12, 18, 29)
    for row in range(horizon, height):
        shade = int(22 + 24 * (row - horizon) / max(height - horizon - 1, 1))
        frame[row] = (shade, shade + 4, shade + 5)
    # Maze headings are 0=north, 1=east, 2=south, 3=west.
    base_angle = (heading - 1) * math.pi / 2
    grid_height, grid_width = len(grid), len(grid[0])
    for column in range(width):
        fraction = (column + 0.5) / width - 0.5
        angle = base_angle + fraction * field_of_view
        distance = 0.05
        portal_distance: float | None = None
        while distance < max_distance:
            sx = int(round(x + math.cos(angle) * distance))
            sy = int(round(y + math.sin(angle) * distance))
            if sy < 0 or sy >= grid_height or sx < 0 or sx >= grid_width:
                break
            cell = grid[sy][sx]
            if cell == "E" and portal_distance is None:
                # The exit is a traversable floor cell. Remember it for a
                # luminous outline, but continue the ray to the wall behind it.
                portal_distance = distance
            if cell == "#":
                break
            distance += 0.05
        corrected = max(0.15, distance * math.cos(fraction * field_of_view))
        wall_height = min(height, int(height / corrected))
        top = max(0, horizon - wall_height // 2); bottom = min(height, horizon + wall_height // 2)
        brightness = max(35, int(225 / (1.0 + corrected * 0.16)))
        color = (brightness, int(brightness * 0.88), int(brightness * 0.72))
        frame[top:bottom, column] = color
        if portal_distance is not None:
            portal_corrected = max(
                0.15, portal_distance * math.cos(fraction * field_of_view)
            )
            portal_height = min(height, max(4, int(height / portal_corrected)))
            portal_top = max(0, horizon - portal_height // 2)
            portal_bottom = min(height, horizon + portal_height // 2)
            thickness = min(2, max(1, (portal_bottom - portal_top) // 4))
            # Only the frame glows; the open centre still shows the space and
            # wall behind the portal, unlike the old opaque exit surface.
            frame[portal_top : portal_top + thickness, column] = PORTAL_COLOR
            frame[portal_bottom - thickness : portal_bottom, column] = PORTAL_COLOR
    return frame
