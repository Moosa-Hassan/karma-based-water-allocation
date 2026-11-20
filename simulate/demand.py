"""Demand, valuation and bid terms following Hassan et al. (2021)."""
import numpy as np
from .mechanism import Mechanism
from .proposed import allocate_social_welfare


def beta_from_efficiency(efficiency_percent: float) -> float:
    """Irrigation coefficient beta = 100 / x for x% application efficiency."""
    if not 0 < efficiency_percent <= 100:
        raise ValueError("efficiency_percent must be in (0, 100]")
    return 100.0 / efficiency_percent


def calculate_demand(
    theta: np.ndarray,
    theta_max: np.ndarray | float,
    area_acres: np.ndarray,
    gross_depth_mm: np.ndarray,
    beta: np.ndarray | float = 1.25,
) -> np.ndarray:
    """Eq. 4: d_n = beta * (theta_max_n - theta_n) * A_n * l_n."""
    theta = np.asarray(theta, dtype=float)
    theta_max = np.asarray(theta_max, dtype=float)
    area_acres = np.asarray(area_acres, dtype=float)
    gross_depth_mm = np.asarray(gross_depth_mm, dtype=float)
    beta = np.asarray(beta, dtype=float)

    if np.any(beta < 1.0):
        raise ValueError(
            "beta must be >= 1 (Hassan et al.: beta = 100/x for x% efficiency); "
            "use beta_from_efficiency(), e.g. 80% efficiency -> beta = 1.25"
        )
    if np.any(area_acres <= 0) or np.any(gross_depth_mm <= 0):
        raise ValueError("areas and irrigation depths must be positive")
    if np.any((theta < 0) | (theta > 1)) or np.any((theta_max <= 0) | (theta_max >= 1)):
        raise ValueError("soil moisture values must lie in [0, 1] and theta_max in (0, 1)")

    deficit = np.maximum(0.0, theta_max - theta)
    return beta * deficit * area_acres * gross_depth_mm


def calculate_monetary_willingness(
    groundwater_cost: float,
    demand: np.ndarray,
    area_acres: np.ndarray,
) -> np.ndarray:
    """Eq. 6: true per-unit valuation v_n = C_g * d_n / A_n."""
    demand = np.asarray(demand, dtype=float)
    area_acres = np.asarray(area_acres, dtype=float)

    if groundwater_cost < 0 or demand.shape != area_acres.shape:
        raise ValueError("invalid valuation inputs")
    if np.any(area_acres <= 0) or np.any(demand < 0):
        raise ValueError("areas must be positive and demands non-negative")

    return groundwater_cost * demand / area_acres


calculate_valuation = calculate_monetary_willingness


def calculate_willingness_to_pay(
    claimed_value: np.ndarray,
    demand: np.ndarray,
) -> np.ndarray:
    """Eq. 7: p_n = v_hat_n * d_n."""
    claimed_value = np.asarray(claimed_value, dtype=float)
    demand = np.asarray(demand, dtype=float)

    if claimed_value.shape != demand.shape:
        raise ValueError("claimed_value and demand must match")
    if np.any(claimed_value < 0) or np.any(demand < 0):
        raise ValueError("claimed values and demands must be non-negative")

    return claimed_value * demand


def truthful_bid(
    groundwater_cost: float,
    demand: np.ndarray,
    area_acres: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Bid pair b_n = (v_hat_n, d_n) with v_hat_n = v_n."""
    value = calculate_monetary_willingness(groundwater_cost, demand, area_acres)
    return value, np.asarray(demand, dtype=float)


def calculate_social_value(
    theta: np.ndarray,
    theta_min: float,
    theta_max: float,
    demand: np.ndarray,
    groundwater_cost: float,
    stress_weight: float = 1.0,
) -> np.ndarray:
    """Per-farm welfare weight combining avoided groundwater expense with urgency."""
    if (
        groundwater_cost < 0
        or stress_weight < 0
        or np.any(np.asarray(theta_max) <= np.asarray(theta_min))
    ):
        raise ValueError("invalid social-value parameters")

    urgency = np.clip((theta_max - np.asarray(theta)) / (theta_max - theta_min), 0.0, 1.0)
    demand = np.asarray(demand, dtype=float)
    return groundwater_cost * (demand > 0) + stress_weight * urgency * demand


class DemandMechanism(Mechanism):
    """Demand-based allocation maximizing social welfare."""

    def allocate(self, demand, canal_supply, week, theta, theta_min, theta_max, stage_weight, active, state):
        # Calculate social value based on demand and crop stage
        social_value = demand * stage_weight + 100.0 * active
        surface, _ = allocate_social_welfare(demand, social_value, canal_supply)
        return surface, state
