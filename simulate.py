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
        f"{'System':<12} {'Social cost':>12} {'Welfare':>12} "
        f"{'GW cost':>12} {'GW used':>12} {'Unmet':>12}"
    )

    for mechanism in mechanisms:
        result = run_simulation(
            num_farmers=args.num_farmers,
            weeks=args.weeks,
            canal_supply_mm=args.canal_supply,
            seed=args.seed,
            mechanism=mechanism,
        )
        print(
            f"{mechanism:<12} {result.social_cost:12.2f} "
            f"{result.social_welfare:12.2f} "
            f"{result.groundwater_cost:12.2f} "
            f"{np.sum(result.groundwater):12.2f} "
            f"{np.sum(result.unmet_demand):12.2f}"
        )


if __name__ == "__main__":
    main()
