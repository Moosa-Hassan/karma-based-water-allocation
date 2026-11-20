"""Traditional area-proportional Warabandi schedule."""
import numpy as np
from .mechanism import Mechanism


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
    discharge_acre_mm_per_hour: float,
    area_acres: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return scheduled delivery and unused runoff for one rotation.

    Args:
        demand: Farmer demand in acre-mm
        turn_hours: Scheduled turn hours per farmer
        discharge_acre_mm_per_hour: Canal discharge in acre-mm/hour
        area_acres: Farm areas in acres

    Returns:
        used: Water actually used (acre-mm)
        runoff: Unused water (acre-mm)
    """
    demand = np.asarray(demand, dtype=float)
    turn_hours = np.asarray(turn_hours, dtype=float)
    area_acres = np.asarray(area_acres, dtype=float)

    if demand.shape != turn_hours.shape or discharge_acre_mm_per_hour < 0:
        raise ValueError("demand and turn_hours must match and discharge must be non-negative")

    # Scheduled delivery in mm (depth)
    scheduled_mm = turn_hours * discharge_acre_mm_per_hour / np.sum(area_acres)

    # Convert to acre-mm (volume) by multiplying by area
    scheduled_acre_mm = scheduled_mm * area_acres

    used = np.minimum(scheduled_acre_mm, np.maximum(demand, 0.0))
    return used, np.maximum(0.0, scheduled_acre_mm - used)


class WarabandiMechanism(Mechanism):
    """Traditional area-proportional Warabandi schedule."""

    def __init__(self, num_farmers: int, area: np.ndarray):
        super().__init__(num_farmers, area)
        self.turn_hours = calculate_turn_schedule(area)

    def allocate(self, demand, canal_supply, week, theta, theta_min, theta_max, stage_weight, active, state):
        # canal_supply is total weekly acre-mm. Discharge is acre-mm per hour (168 hours/week).
        discharge = canal_supply / 168.0
        surface, _ = allocate_warabandi(demand, self.turn_hours, discharge, self.area)
        return surface, state
