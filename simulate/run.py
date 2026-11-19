"""Three-system wheat simulation: Warabandi, demand-based, and Karma welfare."""

from dataclasses import dataclass

import numpy as np

from .demand import (
    calculate_demand,
    calculate_monetary_willingness,
    calculate_social_value,
)
from .proposed import allocate_karma_welfare, allocate_social_welfare
from .soil_moisture import SoilMoistureModel
from .warabandi import allocate_warabandi, calculate_turn_schedule


@dataclass
class SimulationResult:
    soil_moisture: np.ndarray
    surface_water: np.ndarray
    groundwater: np.ndarray
    social_welfare: float
    groundwater_cost: float
    unmet_demand: np.ndarray
    moisture_stress: np.ndarray
    groundwater_stock: np.ndarray
    karma_history: np.ndarray
    final_karma: np.ndarray


def run_simulation(
    num_farmers: int = 24,
    weeks: int = 24,
    canal_supply_mm: float = 30.0,
    seed: int = 42,
    mechanism: str = "proposed",
    irrigation_efficiency_percent: float = 80.0,
) -> SimulationResult:
    """Run a reproducible wheat season under one of three mechanisms."""
    if num_farmers < 1 or weeks < 1 or canal_supply_mm < 0:
        raise ValueError("num_farmers and weeks must be positive; supply must be non-negative")
    if not 0 < irrigation_efficiency_percent <= 100:
        raise ValueError("irrigation_efficiency_percent must be greater than 0 and at most 100")
    if mechanism not in {"warabandi", "demand", "proposed"}:
        raise ValueError("mechanism must be 'warabandi', 'demand', or 'proposed'")

    rng = np.random.default_rng(seed)
    model = SoilMoistureModel(root_zone_depth_mm=800.0)
    area = rng.uniform(5.0, 20.0, num_farmers)
    beta = np.full(
        num_farmers,
        100.0 / irrigation_efficiency_percent,
        dtype=float,
    )
    theta = rng.uniform(model.theta_min, model.theta_max, num_farmers)
    pump_capacity = rng.uniform(40.0, 80.0, num_farmers)
    sowing_offset = rng.integers(-4, 5, num_farmers)
    turn_hours = calculate_turn_schedule(area)
    karma = np.full(num_farmers, 10, dtype=int)

    groundwater_stock = 5000.0
    groundwater_initial = groundwater_stock
    groundwater_floor = 500.0
    percolation_efficiency = 0.20
    groundwater_cost_base = 0.10
    drawdown_alpha = 0.50

    moisture_history = [theta.copy()]
    surface_history = []
    groundwater_history = []
    unmet_history = []
    stress_history = []
    karma_history = [karma.copy()]
    groundwater_stock_history = [groundwater_stock]
    social_welfare = 0.0
    groundwater_cost = 0.0
    canal_supply_acre_mm = canal_supply_mm * float(np.sum(area))

    for week in range(1, weeks + 1):
        rainfall = float(rng.exponential(5.0) if rng.random() > 0.70 else 0.0)
        crop_age = week - sowing_offset
        active = crop_age < 24

        root_depth = model.wheat_root_depth_mm(crop_age)
        demand = calculate_demand(
            theta,
            model.theta_max,
            area,
            root_depth,
            beta,
        )
        demand[~active] = 0.0

        value = calculate_social_value(
            theta,
            model.theta_min,
            model.theta_max,
            demand,
            groundwater_cost_base,
            stress_weight=1.0,
        )
        monetary_willingness = calculate_monetary_willingness(
            groundwater_cost_base,
            demand,
            area,
        )
        stage_weight = model.stress_weight(crop_age)

        if mechanism == "warabandi":
            surface = allocate_warabandi(
                demand,
                turn_hours,
                canal_supply_acre_mm / 168.0,
            )[0]
        elif mechanism == "demand":
            surface = allocate_social_welfare(
                demand,
                demand * stage_weight + 100.0 * active,
                canal_supply_acre_mm,
            )[0]
        else:
            surface, payment, karma, karma_bid, vcg_charge = allocate_karma_welfare(
                demand,
                monetary_willingness,
                karma,
                canal_supply_acre_mm,
                week,
                urgency=stage_weight * np.maximum(
                    0.0,
                    (model.theta_max - theta)
                    / (model.theta_max - model.theta_min),
                ),
                theta=theta,
                theta_min=model.theta_min,
                theta_max=model.theta_max,
            )
            _ = payment, karma_bid, vcg_charge

        unmet_before_groundwater = np.maximum(0.0, demand - surface)
        available = max(0.0, groundwater_stock - groundwater_floor)
        groundwater = np.minimum(unmet_before_groundwater, pump_capacity)
        groundwater = np.minimum(groundwater, available)
        groundwater_total = float(np.sum(groundwater))
        if groundwater_total > available and groundwater_total > 0:
            groundwater *= available / groundwater_total

        kc = model.wheat_coefficients(crop_age)
        et0 = 15.0 + 15.0 * week / weeks
        theta = theta * np.exp(-model.percolation_rate)
        theta -= kc * et0 / model.root_zone_depth_mm
        theta += ((surface + groundwater) / beta + rainfall) / model.root_zone_depth_mm
        theta = np.clip(theta, 0.0, model.theta_max)

        percolation = np.maximum(0.0, model.percolation_rate * theta)
        recharge = percolation_efficiency * float(np.sum(percolation * area * root_depth))
        groundwater_stock = max(
            groundwater_floor,
            groundwater_stock + recharge - np.sum(groundwater),
        )
        drawdown = np.clip(
            (groundwater_initial - groundwater_stock) / groundwater_initial,
            0.0,
            1.0,
        )
        current_cost = groundwater_cost_base * (1.0 + drawdown_alpha * drawdown)
        groundwater_cost += float(current_cost * np.sum(groundwater))

        total_water = surface + groundwater
        unmet = np.maximum(0.0, demand - total_water)
        stress = stage_weight * np.maximum(0.0, model.theta_min - theta)
        social_welfare += float(
            np.sum(value * total_water)
            - np.sum(current_cost * groundwater)
            - np.sum(stress)
        )

        surface_history.append(surface)
        groundwater_history.append(groundwater)
        moisture_history.append(theta.copy())
        unmet_history.append(unmet)
        stress_history.append(stress)
        karma_history.append(karma.copy())
        groundwater_stock_history.append(groundwater_stock)

    return SimulationResult(
        soil_moisture=np.asarray(moisture_history),
        surface_water=np.asarray(surface_history),
        groundwater=np.asarray(groundwater_history),
        social_welfare=social_welfare,
        groundwater_cost=groundwater_cost,
        unmet_demand=np.asarray(unmet_history),
        moisture_stress=np.asarray(stress_history),
        groundwater_stock=np.asarray(groundwater_stock_history),
        karma_history=np.asarray(karma_history),
        final_karma=karma.copy(),
    )
