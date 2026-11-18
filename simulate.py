import argparse

import matplotlib.pyplot as plt
import numpy as np


class WheatDynamics:
    """Wheat soil-moisture dynamics with farmer-specific growth rates."""

    def __init__(self, total_weeks=16):
        if total_weeks < 1:
            raise ValueError("total_weeks must be at least 1")
        self.total_weeks = total_weeks
        self.Z_r = 800.0
        self.theta_max = 0.25
        self.theta_min = 0.10
        self.beta = 1.2
        self.c_weekly = 0.01

    def get_crop_coefficient(self, week, growth_rate):
        progress = np.clip(
            growth_rate * week / self.total_weeks, 0.0, 1.0
        )
        kc = np.full_like(progress, 0.3, dtype=float)

        initial = progress <= 0.25
        development = (progress > 0.25) & (progress <= 0.625)
        late = (progress > 0.625) & (progress <= 0.875)

        kc[initial] = 0.3 + 1.6 * progress[initial]
        kc[development] = 1.15
        kc[late] = 1.15 - 3.4 * (progress[late] - 0.625)
        return kc

    def get_reference_et(self, week):
        return 15.0 + 15.0 * week / self.total_weeks

    def calculate_demand(
        self, theta, theta_max, area, application_efficiency
    ):
        deficit = np.maximum(0.0, theta_max - theta)
        irrigation_depth = self.Z_r / application_efficiency
        return self.beta * deficit * area * irrigation_depth

    def update_soil_moisture(
        self,
        theta,
        retained_water,
        rain_mm,
        week,
        theta_max,
        area,
        application_efficiency,
        growth_rate,
    ):
        kc = self.get_crop_coefficient(week, growth_rate)
        et0 = self.get_reference_et(week)

        theta_after_percolation = theta * np.exp(-self.c_weekly)
        theta_after_et = theta_after_percolation - (kc * et0) / self.Z_r

        effective_root_zone_water = (
            retained_water
            * application_efficiency
            / self.beta
            / area
        )
        theta_new = theta_after_et + (
            effective_root_zone_water + rain_mm
        ) / self.Z_r
        return np.clip(theta_new, 0.0, theta_max)


def distribute_karma(pool, recipients, week):
    """Distribute integer karma to recipients, rotating indivisible points."""
    redistribution = np.zeros_like(recipients, dtype=int)
    recipient_indices = np.flatnonzero(recipients)
    if not len(recipient_indices) or pool == 0:
        return redistribution

    base, remainder = divmod(pool, len(recipient_indices))
    redistribution[recipient_indices] = base
    if remainder:
        start = (week - 1) % len(recipient_indices)
        for offset in range(remainder):
            index = recipient_indices[(start + offset) % len(recipient_indices)]
            redistribution[index] += 1
    return redistribution

def run_simulation(
    num_farmers=3,
    weeks=16,
    initial_karma=10,
    canal_supply_mm=300.0, # Increased slightly for 3-5 farmers
    seed=42,
):
    if num_farmers < 1: raise ValueError("num_farmers must be at least 1")
    if weeks < 1: raise ValueError("weeks must be at least 1")
    
    np.random.seed(seed)
    print(f"--- Wheat Karma Simulation: {num_farmers} farmers, {weeks} weeks ---")
    crop = WheatDynamics(total_weeks=weeks)

    # Heterogeneity
    theta_max = np.full(num_farmers, crop.theta_max)
    area = np.random.uniform(3.0, 5.0, num_farmers)
    application_efficiency = np.random.uniform(0.70, 0.85, num_farmers)
    growth_rate = np.random.uniform(0.85, 1.15, num_farmers)
    # Individual groundwater pumping capacity (mm/week) - replaces shared pool
    gw_pump_capacity = np.random.uniform(40.0, 80.0, num_farmers) 
    
    theta = np.random.uniform(0.12, 0.20, num_farmers)
    karma = np.full(num_farmers, int(initial_karma), dtype=int)

    # Metrics tracking
    groundwater_used = np.zeros(num_farmers)
    groundwater_cost = np.zeros(num_farmers) # NEW: Track cost
    surface_used = np.zeros(num_farmers)
    moisture_history, karma_history = [], []
    
    C_g = 10.0 # Cost per mm of groundwater pumped (from Hassan et al.)

    for week in range(1, weeks + 1):
        rain_mm = np.random.exponential(scale=5.0) if np.random.rand() > 0.7 else 0.0
        
        demand = crop.calculate_demand(theta, theta_max, area, application_efficiency)
        value = demand # Urgency signal

        urgency = np.maximum(0.0, (theta_max - theta) / (theta_max - crop.theta_min))
        bids = np.minimum(karma, np.floor(urgency * karma * 0.3)).astype(int)
        scores = (bids + 1.0) * value
        order = np.argsort(-scores)

        canal_allocated = np.zeros(num_farmers)
        remaining_canal = canal_supply_mm

        # 1. Allocate Canal Water (Shared Resource)
        for farmer in order:
            if remaining_canal <= 0: break
            canal_amount = min(demand[farmer], remaining_canal)
            canal_allocated[farmer] = canal_amount
            remaining_canal -= canal_amount

        # 2. Pump Groundwater (Individual Resource, Limited by Pump Capacity)
        unmet_demand = np.maximum(0.0, demand - canal_allocated)
        # Farmers pump up to their unmet demand OR their pump capacity, whichever is lower
        gw_pumped = np.minimum(unmet_demand, gw_pump_capacity) 
        
        total_allocated = canal_allocated + gw_pumped
        
        # Track metrics
        groundwater_used += gw_pumped
        groundwater_cost += gw_pumped * C_g # Cost = Volume * Price
        surface_used += canal_allocated
        
        # Update physical soil moisture
        theta = crop.update_soil_moisture(
            theta, total_allocated, rain_mm, week,
            theta_max, area, application_efficiency, growth_rate
        )

        # 3. Karma Settlement (Standard PBS)
        received_water = total_allocated > 0
        payments = np.where(received_water, bids, 0)
        pool = int(np.sum(payments))
        
        # FIX: Always redistribute to ALL farmers (Standard PBS)
        redistribution_recipients = np.ones(num_farmers, dtype=bool)
        redistribution = distribute_karma(pool, redistribution_recipients, week)
        
        karma = np.maximum(0, karma - payments + redistribution)

        moisture_history.append(theta.copy())
        karma_history.append(karma.copy())
        
        unserved = np.count_nonzero(unmet_demand > 1e-9)
        print(f"Week {week:2d} | Canal: {canal_supply_mm:6.1f} | "
              f"Unmet Demand: {unserved} | Total GW Cost: {np.sum(groundwater_cost):.1f} | "
              f"Karma: {karma}")

    print("\n--- Final Results ---")
    print(f"Total Groundwater Used (mm): {np.round(groundwater_used, 1)}")
    print(f"Total Groundwater Cost (PKR): {np.round(groundwater_cost, 1)}")
    print(f"Total Surface Water Used (mm): {np.round(surface_used, 1)}")
    print(f"Final soil-moisture variance: {np.var(theta):.5f}")
    print(f"Final karma balances: {karma}")

    # Plotting (Same as before)
    weeks_array = np.arange(1, weeks + 1)
    moisture_history = np.asarray(moisture_history)
    karma_history = np.asarray(karma_history)

    figure, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    for farmer in range(num_farmers):
        axes[0].plot(weeks_array, moisture_history[:, farmer], marker="o", label=f"Farmer {farmer + 1}")
        axes[1].plot(weeks_array, karma_history[:, farmer], marker="o", label=f"Farmer {farmer + 1}")
    axes[0].axhline(crop.theta_max, color="r", linestyle="--", label="Maximum moisture")
    axes[0].axhline(crop.theta_min, color="b", linestyle="--", label="Minimum moisture")
    axes[0].set_ylabel("Soil moisture"); axes[1].set_ylabel("Karma"); axes[1].set_xlabel("Week")
    axes[0].set_title("Wheat soil-moisture dynamics"); axes[1].set_title("Integer karma balances")
    for axis in axes:
        axis.legend(ncol=min(6, num_farmers), fontsize=8); axis.grid(alpha=0.3)
    figure.tight_layout()
    plt.show()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Wheat Karma-based Water Allocation"
    )
    parser.add_argument("--num_farmers", type=int, default=3)
    parser.add_argument("--weeks", type=int, default=16)
    parser.add_argument("--canal_supply_mm", type=float, default=50.0)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    run_simulation(
        num_farmers=args.num_farmers,
        weeks=args.weeks,
        canal_supply_mm=args.canal_supply_mm,
        seed=args.seed,
    )
