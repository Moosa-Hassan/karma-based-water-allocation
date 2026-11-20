"""Pure-Karma allocation with proportional payment and equal redistribution."""
import numpy as np
from .mechanism import Mechanism


def allocate_karma(
    demand: np.ndarray,
    karma: np.ndarray,
    surface_supply: float,
    week: int,
    urgency: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Allocate canal water by Karma bid and redistribute paid Karma equally."""
    demand = np.maximum(0.0, np.asarray(demand, dtype=float))
    karma = np.asarray(karma, dtype=int)

    if demand.shape != karma.shape:
        raise ValueError("demand and Karma balances must have matching shapes")
    if surface_supply < 0 or week < 1 or np.any(karma < 0):
        raise ValueError("surface supply and Karma balances must be non-negative")

    if urgency is None:
        normalized_urgency = np.ones_like(demand)
    else:
        normalized_urgency = np.clip(
            np.asarray(urgency, dtype=float),
            0.0,
            1.0,
        )
        if normalized_urgency.shape != demand.shape:
            raise ValueError("urgency must match demand")

    bid = np.minimum(
        karma,
        np.floor(0.30 * normalized_urgency * karma).astype(int),
    )
    bid[demand <= 0.0] = 0

    order = np.lexsort((np.arange(len(demand)), -normalized_urgency, -bid))
    allocation = np.zeros_like(demand)
    remaining = float(surface_supply)

    for farmer in order:
        if remaining <= 0.0:
            break
        allocation[farmer] = min(demand[farmer], remaining)
        remaining -= allocation[farmer]

    fraction = np.divide(
        allocation,
        np.maximum(demand, 1e-12),
        out=np.zeros_like(allocation),
        where=demand > 0,
    )
    payment = np.rint(bid * fraction).astype(int)
    pool = int(payment.sum())
    base, remainder = divmod(pool, len(karma))
    redistribution = np.full(len(karma), base, dtype=int)
    start = (week - 1) % len(karma)
    for offset in range(remainder):
        redistribution[(start + offset) % len(karma)] += 1

    next_karma = np.maximum(0, karma - payment + redistribution)
    return allocation, payment, next_karma, bid


def allocate_social_welfare(
    demand: np.ndarray,
    social_value: np.ndarray,
    surface_supply: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Allocate surface water to the highest marginal social values."""
    demand = np.maximum(0.0, np.asarray(demand, dtype=float))
    social_value = np.asarray(social_value, dtype=float)

    if demand.shape != social_value.shape or surface_supply < 0:
        raise ValueError("demand and social_value must match and supply must be non-negative")

    order = np.argsort(-social_value, kind="stable")
    allocation = np.zeros_like(demand)
    remaining = float(surface_supply)

    for farmer in order:
        if remaining <= 0:
            break
        allocation[farmer] = min(demand[farmer], remaining)
        remaining -= allocation[farmer]

    return allocation, np.maximum(0.0, demand - allocation)


class ProposedMechanism(Mechanism):
    """Proposed Karma-based allocation mechanism."""

    def allocate(self, demand, canal_supply, week, theta, theta_min, theta_max, stage_weight, active, state):
        current_karma = state['karma']

        # Calculate urgency based on soil moisture deficit and crop stage
        urgency = stage_weight * np.maximum(0.0, (theta_max - theta) / (theta_max - theta_min))

        surface, payment, next_karma, karma_bid = allocate_karma(
            demand, current_karma, canal_supply, week, urgency=urgency
        )

        state['karma'] = next_karma
        return surface, state
