"""Compatibility entry point for the modular water-allocation simulation."""

import argparse
import numpy as np

from simulate.run import run_simulation


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare Warabandi, demand-based, and proposed Karma wheat allocation"
    )
    parser.add_argument("--num-farmers", type=int, default=24)
    parser.add_argument("--weeks", type=int, default=17)
    parser.add_argument(
        "--canal-supply",
        type=float,
        default=30.0,
        help="Canal supply depth in mm per week",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--efficiency",
        type=float,
        default=80.0,
        help="Irrigation efficiency percentage x; beta is 100/x",
    )
    parser.add_argument(
        "--mechanism",
        choices=("warabandi", "demand", "proposed", "all"),
        default="all",
    )
    args = parser.parse_args()
    mechanisms = (
        ("warabandi", "demand", "proposed")
        if args.mechanism == "all"
        else (args.mechanism,)
    )

    print("Mechanism comparison")
    print(
        f"{'System':<12} {'Welfare':>12} {'GW cost':>12} "
        f"{'GW used':>12} {'Unmet':>12} {'Gini':>12}"
    )
    for mechanism in mechanisms:
        result = run_simulation(
            num_farmers=args.num_farmers,
            weeks=args.weeks,
            canal_supply_mm=args.canal_supply,
            seed=args.seed,
            mechanism=mechanism,
            irrigation_efficiency_percent=args.efficiency,
        )
        water_received = np.sum(
            result.surface_water + result.groundwater,
            axis=0,
        )
        ordered = np.sort(water_received)
        total = float(np.sum(ordered))
        if total > 0:
            n = len(ordered)
            gini = float(
                np.sum((2 * np.arange(1, n + 1) - n - 1) * ordered)
                / (n * total)
            )
        else:
            gini = 0.0
        print(
            f"{mechanism:<12} {result.social_welfare:12.2f} "
            f"{result.groundwater_cost:12.2f} "
            f"{np.sum(result.groundwater):12.2f} "
            f"{np.sum(result.unmet_demand):12.2f} "
            f"{gini:12.4f}"
        )


if __name__ == "__main__":
    main()
