"""Three-system wheat simulation: Warabandi, demand-based, and Karma welfare."""
from dataclasses import dataclass
import numpy as np
from .demand import calculate_demand, calculate_social_value
from .soil_moisture import SoilMoistureModel
from .mechanism import Mechanism
from .warabandi import WarabandiMechanism
from .demand import DemandMechanism
from .proposed import ProposedMechanism


@dataclass
class SimulationResult:
    soil_moisture: np.ndarray
    surface_water: np.ndarray
    groundwater: np.ndarray
    social_welfare: float
    social_cost: float
    groundwater_cost: float
    unmet_demand: np.ndarray
    moisture_stress: np.ndarray
    groundwater_stock: np.ndarray
    karma_history: np.ndarray
    final_karma: np.ndarray


def run_simulation(
    num_farmers: int = 24,
    weeks: int = 17,
    canal_supply_mm: float = 30.0,
    seed: int = 42,
    mechanism: str = "proposed",
    beta: float = 1.25,
) -> SimulationResult:
    """Run a reproducible wheat season under one of three mechanisms."""
    if num_farmers < 1 or weeks < 1 or canal_supply_mm < 0:
        raise ValueError("num_farmers and weeks must be positive; supply must be non-negative")
    if beta < 1.0:
        raise ValueError("beta must be >= 1 (Hassan et al.: beta = 100/x for x% efficiency)")
    if mechanism not in {"warabandi", "demand", "proposed"}:
        raise ValueError("mechanism must be 'warabandi', 'demand', or 'proposed'")

    rng = np.random.default_rng(seed)
    model = SoilMoistureModel(root_zone_depth_mm=800.0, beta=beta)

    # Initialize environment
    area = rng.uniform(5.0, 20.0, num_farmers)
    theta_wp = rng.uniform(0.08, 0.12, num_farmers)
    theta_fc = rng.uniform(0.24, 0.30, num_farmers)
    theta = (theta_wp + theta_fc) / 2.0
    beta_values = np.full(num_farmers, beta, dtype=float)
    pump_capacity = rng.uniform(400.0, 800.0, num_farmers)  # acre-mm (scaled by area)

    # Instantiate the chosen mechanism
    if mechanism == "warabandi":
        mech = WarabandiMechanism(num_farmers, area)
    elif mechanism == "demand":
        mech = DemandMechanism(num_farmers, area)
    else:
        mech = ProposedMechanism(num_farmers, area)

    # Initialize state and aquifer
    state = {'karma': np.full(num_farmers, 10, dtype=int)}

    groundwater_stock = 5000.0
    groundwater_initial = groundwater_stock
    groundwater_floor = 500.0
    percolation_efficiency = 0.20
    groundwater_cost_base = 0.10
    drawdown_alpha = 0.50

    # History trackers
    moisture_history = [theta.copy()]
    surface_history = []
    groundwater_history = []
    unmet_history = []
    stress_history = []
    karma_history = [state['karma'].copy()]
    groundwater_stock_history = [groundwater_stock]

    social_welfare = 0.0
    groundwater_cost = 0.0
    social_cost = 0.0
    canal_supply_acre_mm = canal_supply_mm * float(np.sum(area))

    # Weekly simulation loop
    for week in range(1, weeks + 1):
        rainfall_mm = float(rng.exponential(5.0) if rng.random() > 0.70 else 0.0)
        crop_age = np.full(num_farmers, week, dtype=float)
        active = crop_age < 24
        root_depth = model.wheat_root_depth_mm(crop_age)

        # Calculate physical demand (acre-mm)
        demand = calculate_demand(theta, theta_fc, area, root_depth, beta_values)
        demand[~active] = 0.0

        # Calculate social value for accounting
        value = calculate_social_value(
            theta, theta_wp, theta_fc, demand, groundwater_cost_base, stress_weight=1.0
        )
        stage_weight = model.stress_weight(crop_age)

        # Allocation (delegated to the mechanism)
        surface, state = mech.allocate(
            demand=demand,
            canal_supply=canal_supply_acre_mm,
            week=week,
            theta=theta,
            theta_min=theta_wp,
            theta_max=theta_fc,
            stage_weight=stage_weight,
            active=active,
            state=state
        )
        karma = state['karma']

        # Groundwater pumping
        unmet_before_groundwater = np.maximum(0.0, demand - surface)
        available = max(0.0, groundwater_stock - groundwater_floor)
        groundwater = np.minimum(unmet_before_groundwater, pump_capacity)
        groundwater = np.minimum(groundwater, available)

        groundwater_total = float(np.sum(groundwater))
        if groundwater_total > available and groundwater_total > 0:
            groundwater *= available / groundwater_total

        # Soil moisture dynamics
        # Convert surface and groundwater from acre-mm to mm (depth)
        irrigation_mm = (surface + groundwater) / area
        rainfall_array = np.full(num_farmers, rainfall_mm)

        balance = model.update(
            theta=theta,
            irrigation_mm=irrigation_mm,
            rainfall_mm=rainfall_array,
            root_depth_mm=root_depth,
            crop_age_weeks=crop_age,
            total_weeks=weeks,
            week=week,
        )
        theta = balance.theta

        # Aquifer recharge (acre-mm)
        recharge = percolation_efficiency * float(np.sum(balance.drainage_mm * area))

        groundwater_stock = max(
            groundwater_floor,
            groundwater_stock + recharge - np.sum(groundwater),
        )

        # Accounting and costs
        drawdown = np.clip(
            (groundwater_initial - groundwater_stock) / groundwater_initial, 0.0, 1.0
        )
        current_cost = groundwater_cost_base * (1.0 + drawdown_alpha * drawdown)
        groundwater_cost += float(current_cost * np.sum(groundwater))

        total_water = surface + groundwater
        unmet = np.maximum(0.0, demand - total_water)
        stress = stage_weight * (1.0 - balance.ks)  # Water-stress penalty

        social_cost += float(
            np.sum(current_cost * groundwater) + np.sum(unmet) + np.sum(stress)
        )
        social_welfare += float(
            np.sum(value * total_water)
            - np.sum(current_cost * groundwater)
            - np.sum(unmet)
            - np.sum(stress)
        )

        # Update histories
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
        social_cost=social_cost,
        groundwater_cost=groundwater_cost,
        unmet_demand=np.asarray(unmet_history),
        moisture_stress=np.asarray(stress_history),
        groundwater_stock=np.asarray(groundwater_stock_history),
        karma_history=np.asarray(karma_history),
        final_karma=karma.copy(),
    )
