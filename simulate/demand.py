"""Demand and welfare terms derived from the sensor-based model."""

import numpy as np


def calculate_demand(
    theta: np.ndarray,
    theta_max: float,
    area_acres: np.ndarray,
    gross_depth_mm: np.ndarray,
    beta: np.ndarray | float = 1.2,
) -> np.ndarray:
    """Equation 4: gross water required to restore field capacity."""
    theta = np.asarray(theta, dtype=float)
    area_acres = np.asarray(area_acres, dtype=float)
    gross_depth_mm = np.asarray(gross_depth_mm, dtype=float)
    beta = np.asarray(beta, dtype=float)
    if np.any(beta < 1) or np.any(area_acres <= 0) or np.any(gross_depth_mm <= 0):
        raise ValueError("beta must be at least 1 and areas/depths must be positive")
    deficit = np.maximum(0.0, theta_max - theta)
    return beta * deficit * area_acres * gross_depth_mm


def calculate_social_value(
    theta: np.ndarray,
    theta_min: float,
    theta_max: float,
    demand: np.ndarray,
    groundwater_cost: float,
    stress_weight: float = 1.0,
) -> np.ndarray:
    """Estimate marginal social value for ranking scarce surface water.

    The value combines avoided groundwater expense with the cost of moisture
    stress. This makes the proposed allocation an explicit welfare objective.
    """
    if groundwater_cost < 0 or stress_weight < 0 or theta_max <= theta_min:
        raise ValueError("invalid social-value parameters")
    urgency = np.clip((theta_max - np.asarray(theta)) / (theta_max - theta_min), 0.0, 1.0)
    demand = np.asarray(demand, dtype=float)
    return groundwater_cost * (demand > 0) + stress_weight * urgency * demand


def calculate_monetary_willingness(
    groundwater_cost: float,
    demand: np.ndarray,
    area_acres: np.ndarray,
) -> np.ndarray:
    """True per-farm willingness to pay: Cg * demand / area."""
    demand = np.asarray(demand, dtype=float)
    area_acres = np.asarray(area_acres, dtype=float)
    if groundwater_cost < 0 or demand.shape != area_acres.shape:
        raise ValueError("invalid monetary willingness inputs")
    if np.any(area_acres <= 0):
        raise ValueError("areas must be positive")
    return groundwater_cost * demand / area_acres
