"""Traditional area-proportional Warabandi schedule."""

import numpy as np


def calculate_turn_schedule(
    area_acres: np.ndarray,
    filling_hours: np.ndarray | None = None,
    draining_hours: np.ndarray | None = None,
    cycle_hours: float = 168.0,
) -> np.ndarray:
    """Implement the Warabandi unit-time and farmer-turn equations."""
    area = np.asarray(area_acres, dtype=float)
    if np.any(area <= 0) or cycle_hours <= 0:
        raise ValueError("areas and cycle_hours must be positive")
    filling = np.zeros_like(area) if filling_hours is None else np.asarray(filling_hours, dtype=float)
    draining = np.zeros_like(area) if draining_hours is None else np.asarray(draining_hours, dtype=float)
    if filling.shape != area.shape or draining.shape != area.shape:
        raise ValueError("delay arrays must match area_acres")
    command_area = float(np.sum(area))
    unit_time = (cycle_hours - np.sum(filling) + np.sum(draining)) / command_area
    return np.maximum(0.0, unit_time * area + filling - draining)


def allocate_warabandi(
    demand: np.ndarray,
    turn_hours: np.ndarray,
    discharge_mm_per_hour: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Return scheduled delivery and unused runoff for one rotation."""
    demand = np.asarray(demand, dtype=float)
    turn_hours = np.asarray(turn_hours, dtype=float)
    if demand.shape != turn_hours.shape or discharge_mm_per_hour < 0:
        raise ValueError("demand and turn_hours must match and discharge must be non-negative")
    scheduled = turn_hours * discharge_mm_per_hour
    used = np.minimum(scheduled, np.maximum(demand, 0.0))
    return used, np.maximum(0.0, scheduled - used)
