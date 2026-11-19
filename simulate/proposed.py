"""Demand-based allocation that maximizes one-period social welfare."""

import numpy as np


def allocate_karma_welfare(
    demand: np.ndarray,
    monetary_willingness: np.ndarray,
    karma: np.ndarray,
    surface_supply: float,
    week: int,
    alpha: float | None = None,
    urgency: np.ndarray | None = None,
    theta: np.ndarray | None = None,
    theta_min: float = 0.10,
    theta_max: float = 0.25,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Apply the hybrid Karma/VCG priority rule and equal PBS redistribution."""
    demand = np.maximum(0.0, np.asarray(demand, dtype=float))
    monetary_willingness = np.maximum(
        0.0,
        np.asarray(monetary_willingness, dtype=float),
    )
    karma = np.asarray(karma, dtype=int)
    if (
        demand.shape != monetary_willingness.shape
        or monetary_willingness.shape != karma.shape
    ):
        raise ValueError(
            "demand, monetary_willingness, and karma must have matching shapes"
        )
    if surface_supply < 0 or np.any(karma < 0):
        raise ValueError("surface supply and Karma balances must be non-negative")

    if urgency is None:
        if theta is None:
            normalized_urgency = np.ones_like(demand)
        else:
            normalized_urgency = np.clip(
                (theta_max - np.asarray(theta, dtype=float))
                / (theta_max - theta_min),
                0.0,
                1.0,
            )
    else:
        normalized_urgency = np.clip(
            np.asarray(urgency, dtype=float),
            0.0,
            1.0,
        )

    bid = np.minimum(
        karma,
        np.floor(0.30 * normalized_urgency * karma).astype(int),
    )
    if alpha is None:
        mean_karma = max(float(np.mean(np.maximum(karma, 1))), 1.0)
        alpha = float(np.std(monetary_willingness)) / mean_karma

    score = monetary_willingness + alpha * bid
    order = np.lexsort((np.arange(len(demand)), -score))
    allocation = np.zeros_like(demand)
    remaining = float(surface_supply)
    for farmer in order:
        if remaining <= 0.0:
            break
        allocation[farmer] = min(demand[farmer], remaining)
        remaining -= allocation[farmer]

    vcg_charge = np.zeros(len(demand), dtype=float)
    active_bidders = bid > 0
    for farmer in np.flatnonzero((allocation > 0) & ~active_bidders):
        counterfactual_remaining = float(surface_supply)
        counterfactual = np.zeros_like(demand)
        remaining_indices = np.flatnonzero(np.arange(len(demand)) != farmer)
        counterfactual_order = remaining_indices[
            np.argsort(-score[remaining_indices], kind="stable")
        ]
        for index in counterfactual_order:
            if counterfactual_remaining <= 0:
                break
            counterfactual[index] = min(
                demand[index],
                counterfactual_remaining,
            )
            counterfactual_remaining -= counterfactual[index]
        vcg_charge[farmer] = max(
            0.0,
            float(
                np.sum(monetary_willingness * counterfactual)
                - np.sum(
                    monetary_willingness
                    * np.where(np.arange(len(demand)) == farmer, 0.0, allocation)
                )
            ),
        )

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
    return allocation, payment, next_karma, bid, vcg_charge


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
