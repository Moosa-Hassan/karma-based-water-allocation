"""Pure-Karma allocation with proportional payment and equal redistribution."""

import numpy as np


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


allocate_karma_welfare = allocate_karma


def allocate_social_welfare(
    demand: np.ndarray,
    social_value: np.ndarray,
    surface_supply: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Allocate surface water to the highest marginal social values.

    The allocation solves the linear welfare problem
    ``max sum(value[i] * allocation[i])`` subject to each demand and the
    shared supply constraint. Ties are resolved by farmer index.
    """
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
